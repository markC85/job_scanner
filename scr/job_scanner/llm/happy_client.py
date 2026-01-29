from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
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

    You set your 'speed' of the LLM here:


    for torch_dttype use torch.float32 for CPU base and accuracy
    for GPU and less accurate use torch.float16


    Args:
        model_name (str): this is the model to use
        memory_use (dtype):
    """
    model_name = happy_model_options(model_name)

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,# set what model CPU or GPU
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name, token=os.environ["HF_TOKEN"])
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        token=os.environ["HF_TOKEN"],
        quantization_config=bnb_config,
        #device_map="cuda",
    )
    model.eval()
    model = torch.compile(model)
    LOG.info("Local LLM loaded into memory")

    return model_name, tokenizer, model