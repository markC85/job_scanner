import torch
import json
import time
import re
from transformers import AutoModelForCausalLM, AutoTokenizer
from openai import RateLimitError
from job_scanner.utils.logger_setup import start_logger
from job_scanner.llm.prompts import llm_prompt

LOG = start_logger()


def llm_llama():
    model_name = "meta-llama/Llama-2-7b-chat-hf"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",       # automatically puts layers on your GPU
        torch_dtype=torch.float16 # FP16
    )

    prompt = "Rate this job description vs my CV: ..."
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    output = model.generate(**inputs, max_new_tokens=150)
    print(tokenizer.decode(output[0]))


def build_llm_prompt(cv_chunk: str, job_text: str) -> str:
    """
    This will build the llm prompt

    Score	Meaning
    0	No relevance
    1	Very weak / tangential
    2	Some overlap
    3	Good match
    4	Strong match
    5	Directly aligned

    Args:
        cv_chunk (str): this is the cv chunk to be evaluated
        job_text (str): this is the text of the job add to be evaluated

    Returns:
        llm_token (str): this is the LLM prompt to use
    """
    llm_token = f"""
        You are evaluating how closely a CV matches a job description.

        JOB DESCRIPTION:
        \"\"\"
        {job_text}
        \"\"\"

        CV SECTION:
        \"\"\"
        {cv_chunk}
        \"\"\"

        Rate how well this CV section matches the job description.

        Return ONLY valid JSON with this exact schema:
        {{
          "score": integer from 0 to 5,
          "matching_skills": [list of short skill phrases],
          "missing_skills": [list of short skill phrases],
          "reason": "one short sentence"
        }}
        """

    return llm_token

def rate_job_vs_cv(llm_client, cv_chunks: list[str], job_text: str) -> dict:
    """
    This will rate the job description to the cv chunks that are broken up

    Args:
        llm_client: this is the LLM client you use
        cv_chunks (list[str]): this is the list of chunks that are str
        job_text (str): this is the job description as one large string

    Return:
        dict: t his is the result of the comparison
    """
    results = []

    for chunk in cv_chunks:
        result = compare_chunk_with_job(llm_client, chunk, job_text)
        results.append(result)

    # sort best matches first
    results.sort(key=lambda r: r["score"], reverse=True)

    top_results = results[:5]  # only strongest evidence

    avg_score = round(
        sum(r["score"] for r in top_results) / max(len(top_results), 1),
        2
    )

    # get the missing skill found
    missing_skills = sorted(
        set(skill for r in top_results for skill in r["missing_skills"])
    )
    llm_result_dict = {
        "rating_vs_cv": avg_score,
        "top_matches": top_results,
        "missing_skills": missing_skills,
    }

    return llm_result_dict

def compare_chunk_with_job(llm_client, cv_chunk: str, job_text: str) -> dict:
    """
    Compare the chunks of txt with the job description

    Args:
        llm_client : this is the LLM client you choose to use with this
        cv_chunk (str): this is the chunk of the CV to compare agents
        job_text (str): this is the job description text to compare agents

    Returns:
        dict: this is the return data for the comparison
    """
    prompt = build_llm_prompt(cv_chunk, job_text)

    try:
        response = llm_client.chat.completions.create(
            model="gpt-4.1-mini",  # cheap + good enough
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict evaluator. Respond only in JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,  # low variance
        )
    except RateLimitError as e:
        LOG.error(f"LLM quota exhausted or rate-limited. {e}")
        time.sleep(30)
        return {
            "score": 0,
            "matching_skills": [],
            "missing_skills": [],
            "reason": "Quota exhausted",
        }

    content = response.choices[0].message.content

    try:
        return json.loads(content) # strop LLM from looping infinitely
    except json.JSONDecodeError:
        bad_json = {
            "score": 0,
            "matching_skills": [],
            "missing_skills": [],
            "reason": "Invalid LLM response",
        }
        return bad_json

def turn_llm_result_into_dictionary(llm_result: str, required_keys: set) -> dict | None:
    """
    This will return a LLM which brings back a string
    into a dictionary IF you asked the LLM to return
    its results in a dictionary format.

    Args:
        llm_result (str): this is the LLM result you got

    Returns:
        clean_results (dict): this is the result dictionary you asked
                              the LLM to give you back
    """
    text = "".join(llm_result)
    json_blocks = re.findall(r'\{[\s\S]*?\}', text)
    parsed_dicts = []

    for block in json_blocks:
        try:
            parsed_dicts.append(json.loads(block))
        except json.JSONDecodeError:
            pass  # silently skip schema / junk

    if not parsed_dicts:
        LOG.error("We could not find any {...} inside the LLM please make sure you asked for a ditionary back from your LLM")
        return None

    # try to avoid half broken results coming back for bad dictionaries

    clean_results = [
        d for d in parsed_dicts
        if required_keys.issubset(d)
    ]

    if not clean_results:
        LOG.error(f"We could not find any keys in your dictionary that matches {required_keys}")
        return None
    return clean_results