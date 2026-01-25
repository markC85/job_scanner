import torch
import json
from pprint import pprint
from job_scanner.utils.logger_setup import start_logger
from job_scanner.llm.prompts import llm_promt

LOG = start_logger()

class JobRanker:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        LOG.info("JobRanker initialized with local LLM")

    def rate_job_chunk(self, cv_text: str, job_text: str, max_new_tokens: int = 100, temperature: float = 0.1, top_p: float = 0.9)-> str:
        """
        Passes the CV and job description through the LLM and returns the evaluation.

        Returns:
            response (str): this is the response from the LLM model
        """
        # Get the dynamic prompt
        prompt = llm_promt(job_description=job_text, cv_text=cv_text)

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                top_p=top_p,
                temperature=temperature,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        response = self.tokenizer.decode(output[0], skip_special_tokens=True)

        return response