import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from .base import LLMClient
from job_scanner.utils.logger_setup import start_logger

LOG = start_logger()

class LocalHFClient(LLMClient):
    def __init__(self, model_name: str):
        LOG.info(f"Loading local model: {model_name}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
        )

        self.model.eval()
        LOG.info("Local LLM ready")

    def generate(self, prompt: str, max_new_tokens=256, temperature=0.2) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
            )

        return self.tokenizer.decode(output[0], skip_special_tokens=True)