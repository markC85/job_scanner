from openai import OpenAI
import os

def create_llm_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            """
            OPENAI_API_KEY not set. Did you restart your terminal / IDE?
            In power shell run [setx OPENAI_API_KEY "sk-xxxxxxxx"]
            in cmd run [setx OPENAI_API_KEY "sk-xxxxxxxx"]
            """
        )
    return OpenAI(api_key=api_key)