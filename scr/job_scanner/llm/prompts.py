
def llm_prompt(job_description: str, cv_text: str):
    """
    LLM prompt that is used to keep things on rails

    Args:
        job_description (str): this is the job description to compare
        cv_text (str): this is the cv chunks to compare
    """
    job_match_prompt = f"""
    You are an experienced technical recruiter specializing in animation, games, and VFX.
    
    Your task is to evaluate how well a candidate's CV matches a specific job description.
    
    Compare the following two texts:
    
    === Candidate CV ===
    {cv_text}
    
    === Job Description ===
    {job_description}
    
    Evaluate the match using these criteria:
    - Core role alignment (3D animation, seniority, responsibilities)
    - Relevant tools, pipelines, or technical skills
    - Industry/domain relevance (games, film, real-time, etc.)
    - Level of experience implied
    
    Return ONLY a SINGLE JSON object with the following keys and no extra text:
    {{
      "score": float from 0 to 100,
      "missing_skills": list of strings,
      "justification": string (2-4 sentences, concise)
    }}
    
    - "score": number between 0 and 100 indicating fit
    - "missing_skills": skills listed in the job description that are missing from the CV
    - "justification": a concise explanation of the reasoning
    
    Be strict. Do not inflate the score. Do not include explanations or text outside the JSON object.
    """

    return job_match_prompt