#!/usr/bin/env python3
"""
DevOps Helper LLM Fine-Tuning – Python workflow

Runs the same workflow as llm_finetuning_devops.ipynb:
1. Load config from .env (HF_ENDPOINT, HF_TOKEN, JF_MODEL_REPO)
2. Load dataset, fine-tune Qwen 1.5 with LoRA
3. Evaluate and log model to Artifactory

Usage:
    cd notebooks/devops-helper
    conda activate devops-helper
    python run_finetuning.py
"""

import os
from pathlib import Path
from datetime import datetime

# Resolve script directory for .env (works when run from any cwd)
SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)

# Load credentials from .env in this directory
from dotenv import load_dotenv
load_dotenv(SCRIPT_DIR / ".env", override=True)

# HuggingFace / Artifactory config
os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "86400")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "86400")
hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
if hf_token:
    os.environ["HUGGINGFACE_HUB_TOKEN"] = hf_token

JF_MODEL_REPO = os.environ.get("JF_MODEL_REPO", "devops-helper-llms")

if not hf_token:
    print("Note: HF_TOKEN not set – dataset/model downloads will be unauthenticated (rate limits may apply)")

# Model and training config
HUGGINGFACE_MODEL = "Qwen/Qwen1.5-0.5B-Chat"
DATASET_NAME = "Szaid3680/Devops"
new_model_adapter = "qwen-0.5b-devops-adapter"

# Imports (after env is configured)
import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from trl import SFTTrainer
import frogml


def format_instruction(example):
    instruction = example.get("Instruction", "")
    inp = example.get("Prompt", "")
    response = example.get("Response", "")
    return f"<s>[INST] {instruction}\n{inp} [/INST] {response} </s>"


def main():
    print("=== 1. Loading dataset ===")
    dataset = load_dataset(DATASET_NAME, split="train", token=hf_token)
    dataset = dataset.train_test_split(test_size=0.1)
    train_dataset = dataset["train"].select(range(2))
    eval_dataset = dataset["test"].select(range(2))
    print(f"Sample: {train_dataset[0]}")

    print("\n=== 2. Loading tokenizer and model ===")
    tokenizer = AutoTokenizer.from_pretrained(HUGGINGFACE_MODEL, token=hf_token or True)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        HUGGINGFACE_MODEL,
        device_map="cpu",
        token=hf_token or True,
    )

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

    training_args = TrainingArguments(
        output_dir="./qwen-finetuned",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        logging_steps=10,
        max_steps=1,
        eval_strategy="steps",
        eval_steps=1,
        fp16=False,
    )

    print("\n=== 3. Fine-tuning ===")
    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        peft_config=lora_config,
        formatting_func=format_instruction,
        args=training_args,
    )
    train_output = trainer.train()

    print("\n=== 4. Evaluation ===")
    metrics = train_output.metrics
    print("Metrics:", metrics)

    print("\n=== 5. Saving adapter ===")
    trainer.model.save_pretrained(new_model_adapter)

    print("\n=== 6. Comparing fine-tuned vs base model ===")
    base_model = AutoModelForCausalLM.from_pretrained(
        HUGGINGFACE_MODEL, device_map="cpu", token=hf_token or True
    )
    finetuned_model = PeftModel.from_pretrained(base_model, new_model_adapter)
    finetuned_model = finetuned_model.merge_and_unload()

    prompt = "How do I expose a deployment in Kubernetes using a service?"
    messages = [
        {"role": "system", "content": "You are a helpful DevOps assistant."},
        {"role": "user", "content": prompt},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    model_inputs = tokenizer([text], return_tensors="pt").to("cpu")
    input_ids_len = model_inputs["input_ids"].shape[1]

    print("--- FINE-TUNED MODEL ---")
    generated_ids = finetuned_model.generate(model_inputs.input_ids, max_new_tokens=256)
    print(tokenizer.decode(generated_ids[:, input_ids_len:][0], skip_special_tokens=True))

    print("\n--- BASE MODEL ---")
    original_model = AutoModelForCausalLM.from_pretrained(
        HUGGINGFACE_MODEL, device_map="cpu", token=hf_token or True
    )
    generated_ids_base = original_model.generate(model_inputs.input_ids, max_new_tokens=256)
    print(tokenizer.decode(generated_ids_base[:, input_ids_len:][0], skip_special_tokens=True))

    print("\n=== 7. Logging to Artifactory ===")
    version = f"0.0.1-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    try:
        frogml.huggingface.log_model(
            model=finetuned_model,
            tokenizer=tokenizer,
            repository=JF_MODEL_REPO,
            model_name="devops_helper",
            version=version,
            parameters={"finetuning-dataset": DATASET_NAME},
            code_dir="code_dir",
            dependencies=["main/conda.yaml"],
            metrics=metrics,
            predict_file="code_dir/predict.py",
        )
        print(f"--- Model Logged Successfully (version {version}) ---")
    except Exception as e:
        print(f"Model logging failed: {e}")
        raise


if __name__ == "__main__":
    main()
