
def llm_promt(job_description: str, cv_text: str):
    """
    LLM prompt that is used to keep things on rails

    Args:
        job_description (str): this is the job description to compare
        cv_text (str): this is the cv chunks to compare
    """
    JOB_MATCH_PROMPT = f"""
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

    Return:
    1. A match score from 0 to 100
    2. A concise justification (2–4 sentences max)
    3. What skills are missing from the {job_description} compared to the {cv_text} put this together in a list

    Be strict. Do not inflate the score.
    """

    return JOB_MATCH_PROMPT