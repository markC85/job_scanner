from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import os
import json
import torch
from job_scanner.utils.logger_setup import start_logger

LOG = start_logger()

def happy_model_options(model_name:str) -> str:
    """
    This will return the model name for the happy client

    Args:
        model_name (str): this is the name of the model to use. Valid options are "meta_llama", "mistralai", and "NousResearch".

    Returns:
        model (str): this is the model name to use for the happy client
    """
    model_names = {
        # Baseline options (fast, good value)
        "meta_llama": "meta-llama/Llama-2-7b-chat-hf",
        "mistralai": "mistralai/Mistral-7B-Instruct-v0.2",
        "NousResearch": "NousResearch/Nous-Hermes-2-Mistral-7B",
        # Additions (high value)
        "qwen25_7b_instruct": "Qwen/Qwen2.5-7B-Instruct",
        "gemma2_9b": "google/gemma-2-9b",
        # Experimental / heavier / more friction
        "llama4_scout_instruct": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
    }
    model = model_names.get(model_name)

    if not model:
        raise ValueError(f"Unknown model name '{model_name}'. Valid options: {list(model_names.keys())}")

    return model

def set_up_hugging_env_var(json_path) -> None:
    """
    This will set up the Hugging Face environment variable for the happy client

    Args:
        json_path (str): this is the path to the json file containing the Hugging Face token
    """
    if "HF_TOKEN" not in os.environ:
        with open(json_path) as f:
            token = json.load(f).get("hugging_token")
        if not token:
            raise RuntimeError("hugging_token missing from credentials file")
        os.environ["HF_TOKEN"] = token
        LOG.info("HF_TOKEN variable is set up")
    else:
        LOG.info("HF_TOKEN is all ready set up")

def set_up_token(model_name: str) -> tuple[str, AutoTokenizer, AutoModelForCausalLM]:
    """
    Set up the Happy client LLM so I can run it locally
    You set your 'speed' of the LLM here:
    for torch_dttype use torch.float32 for CPU base and accuracy
    for GPU and less accurate use torch.float16

    Args:
        model_name (str): this is the model to use
        memory_use (dtype):

    Returns:
        model_name (str): this is the model name used for the happy client
        tokenizer (AutoTokenizer): this is the tokenizer for the model
        model (AutoModelForCausalLM): this is the model for the happy client
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
        device_map="auto",
    )
    model.eval()
    model = torch.compile(model)
    LOG.info("Local LLM loaded into memory")

    LOG.debug("Model:", model.config._name_or_path)
    LOG.debug("Device:", next(model.parameters()).device)
    LOG.debug("Is CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        # If you see cuda:0 and your GPU name, you’re running it locally on GPU.
        LOG.debug("GPU:", torch.cuda.get_device_name(0))

    return model_name, tokenizer, model