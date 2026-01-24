from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import json
import torch
from job_scanner.utils.logger_setup import start_logger

LOG = start_logger()

def happy_model_options(model_name:str)->str:
    model_names = {
        "meta_llama":"meta-llama/Llama-2-7b-chat-hf",
        "mistralai":"mistralai/Mistral-7B-Instruct-v0.2"
    }

    model = model_names.get(model_name)

    return model

def set_up_hugging_env_var(json_path):
    if "HF_TOKEN" not in os.environ:
        with open(json_path) as f:
            token = json.load(f).get("hugging_token")
        if not token:
            raise RuntimeError("hugging_token missing from credentials file")
        os.environ["HF_TOKEN"] = token
        LOG.info("HF_TOKEN variable is set up")
    else:
        LOG.info("HF_TOKEN is all ready set up")

def set_up_token(model_name: str):
    """
    Set up the Happy client LLM so I can run it locally

    Args:
        model_name (str): this is the model to use
        memory_use (dtype):
    """

    model_name = happy_model_options(model_name)

    tokenizer = AutoTokenizer.from_pretrained(model_name, token=os.environ["HF_TOKEN"])
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        token=os.environ["HF_TOKEN"],
        torch_dtype=torch.float32,
        device_map="auto",
    )
    LOG.info("Local LLM loaded into memory")

    return model_name, tokenizer, model

if __name__ == "__main__":
    json_path = (
        r"D:\storage\programming\python\job_scanner\credentials\open_ai_api_key.json"
    )
    model_name = "mistralai"
    set_up_hugging_env_var(json_path)
    model_name, tokenizer, model = set_up_token(model_name)

    prompt = "Rate this job description against a senior 3D animator CV."

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs, max_new_tokens=100, do_sample=True, temperature=0.1
        )

    print(tokenizer.decode(output[0], skip_special_tokens=True))