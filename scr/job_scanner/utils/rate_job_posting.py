import datetime
import trafilatura
import re
import os
import numpy as np
from job_scanner.utils.logger_setup import start_logger
from job_scanner.utils.web_scrapper_linkedin import access_webpage
from job_scanner.data.job_lookup_data import job_lookup_data
from job_scanner.llm.openai_client import create_llm_client
from job_scanner.llm.job_ranker import JobRanker
from job_scanner.llm.happy_client import set_up_token, set_up_hugging_env_var
from bs4 import BeautifulSoup
from typing import Optional, List
from sentence_transformers import SentenceTransformer

from pypdf import PdfReader

LOG = start_logger()



# Load a small, fast model
EMBEDDING_MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def embed_text(text: str) -> np.ndarray:
    """Return a vector embedding for a piece of text."""
    return EMBEDDING_MODEL.encode(text, convert_to_numpy=True, normalize_embeddings=True)

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Return cosine similarity between two vectors."""
    return float(np.dot(vec1, vec2))

def score_job_vs_cv(cv_chunks: list[str], job_text: str) -> float:
    """
    Returns a similarity score [0.0, 1.0] between the CV and job description.
    """
    job_vec = embed_text(job_text)

    max_score = 0.0
    for chunk in cv_chunks:
        chunk_vec = embed_text(chunk)
        sim = cosine_similarity(chunk_vec, job_vec)
        if sim > max_score:
            max_score = sim

    return max_score

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract text from a PDF file at `path`. Returns an empty string on failure.

    Args:
        pdf_path (str): path to the PDF file to load

    Returns:
        str | None: this is a string of the PDF file
    """
    if not os.path.isfile(pdf_path):
        LOG.error(f"PDF file not found: {pdf_path}")
        return None
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text:
            pages.append(page_text)
    text = "\n\n".join(pages)
    # normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def break_text_into_chunks(text: str, max_chunk_chars: int = 2000, overlap: int = 200) -> List[str]:
    """
    Split `text` into overlapping chunks of up to `max_chunk_chars` characters,
    with `overlap` characters shared between consecutive chunks.

    Args:
        text (str): this is the text you need to chunk up
        max_chunk_chars (int): this is the maximum size of the chunk
        overlap (int): how many characters to overlap the chunks by

    Returns:
        list[str]: this is the list of chunks of text
    """
    chunks = []
    if not text:
        return chunks
    if max_chunk_chars <= 0:
        LOG.debug("max_chunk_chars must be > 0")
        return chunks
    # check invalid overlaps if their below 0 or less
    # than max_chunk_chars it will default to 10% of
    # max_chunk_chars rounded down never negative
    if overlap < 0 or overlap >= max_chunk_chars:
        overlap = max(0, int(max_chunk_chars * 0.1))
    start = 0
    length = len(text)
    while start < length:
        end = min(start + max_chunk_chars, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == length:
            break
        start = max(end - overlap, end) - (0 if overlap == 0 else 0)  # ensure forward progress
        # simpler: move start to end - overlap
        start = end - overlap
    return chunks

def scrape_job_page(url:str) -> Optional[dict]:
    """
    This will scrape a web page for all it's content
    and try to return all readable data in it removing
    anything that is not human-readable or extra

    Args:
        url (str): the ural to scrape from

    Returns:
        response (None | dict): this is the dictionary of the data pulled
                                from the web page if there is nothing
                                it will return None
    """
    # fetch the web page
    response = access_webpage(url)
    if not response:
        return None
    """
    headers = {
        "User-Agent": random.choice(job_lookup_data(2)),
        "Accept-Language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.8"]),
        "Accept": "text/html,application/xhtml+xml",
        "Connection": random.choice(["keep-alive", "close"]),
    }

    response = requests.get(url, headers=headers, timeout=10)
    """
    html = response.text

    # Step 2: Try trafilatura for main content
    main_content = trafilatura.extract(html)

    # Fallback: parse manually if trafilatura fails
    if not main_content:
        soup = BeautifulSoup(html, "html.parser")
        # Remove scripts/styles
        for tag in soup.find_all(job_lookup_data(3)):
            tag.decompose()

        # Extract headings + paragraphs
        sections = []
        for elem in soup.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
            text = elem.get_text(strip=True)
            if text:
                sections.append(text)
        main_content = "\n".join(sections)

    # Step 4: Create LLM-friendly JSON
    job_data = {"url": url, "content": main_content}
    return job_data

def update_google_sheet_with_job_rating():
    pass



def normalize_text(text:str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def matches_job_interest(job_title: str, text: str, keywords_include: frozenset, keywords_exclude: frozenset) -> bool:
    """
    This will look through a glock of text and check
    to make sure that it has a word that matches
    inside your keywords_include list

    Args:
        job_title (str): this is the job title found in the add beforehand
        text (str): the text to check for the words
        keywords_include (frozenset): set of words to compare agents you want in the text
        keywords_exclude (frozenset): set of words to compare agents you don't want in the text
    """
    text = normalize_text(text)
    job_title = normalize_text(job_title)
    if not any(kw in text for kw in keywords_include) and not any(kw in job_title for kw in keywords_include):
        LOG.debug("We did not find any for the keywords_include in the text")
        return False
    if any(kw in text for kw in keywords_exclude):
        return False
    return True



def rate_job_posts(job_links: list, pdf_file_path: str, json_token_path: str, llm_model: str = "mistralai"):
    """
    This will rate all the job links that are passed comparing them to a cv to see
    if there close to what you do and looking for keywords

    Args:
        job_links (list): this is the jobs
        pdf_file_path (str): a path to the pdf file that is your CV
        llm_model (str): this is the LLM you are using
        json_token_path (str): This is the path to the LLM token you need to inishiate it
    """
    upload_to_google_sheets = []
    llm_client = create_llm_client()
    # extract the text from a PDF CV file and chunk it for LLM comparison
    cv_text = extract_text_from_pdf(pdf_file_path)
    cv_chunks = break_text_into_chunks(cv_text, max_chunk_chars=1800, overlap=200)
    LOG.debug(f"Extracted {len(cv_chunks)} cv chunks for comparison")
    set_up_hugging_env_var(json_token_path)
    model_name, tokenizer, model = set_up_token(llm_model)

    # scrape each link from the job_links list and get all the data off each page
    for job in job_links:
        LOG.debug(f"Checking {job['jog_title']}")
        google_sheet_data = {
            "job_id": job["job_id"],
            "rating_vs_cv": '',
            "missing_skills": '',
            "jog_title": job["jog_title"],
            "company": job["company"],
            "location": job["location"],
            "link": job["link"],
            "date_processed": datetime.datetime.now().strftime("%m/%d/%Y"),
            "cv_used": pdf_file_path,
            "scraped_failed": 'No',
            "no_matching_job_title": '',
            "content": '',
            "cv_chunk_count": len(cv_chunks)
        }
        website_info = scrape_job_page(job["link"])
        if not website_info:
            LOG.info(f"We where not able to scrape anything from job {job['job_id']}")
            google_sheet_data['scraped_success']='Yes'
            upload_to_google_sheets.append(google_sheet_data)
            continue

        # check to see if the JOB TITTLE fits inside my job title in my keyword set
        job_matches_text = matches_job_interest(
            job_title = job["jog_title"],
            text = website_info["content"],
            keywords_include = job_lookup_data(1),
            keywords_exclude = job_lookup_data(4)
        )

        if not job_matches_text:
            LOG.debug(
                "The job description either did not have the job title I am looking for or had one of ignore words in it"
            )
            google_sheet_data["no_matching_job_title"] = "Yes"
            upload_to_google_sheets.append(google_sheet_data)
            continue

        google_sheet_data["content"] = website_info["content"]
        google_sheet_data["no_matching_job_title"] = "No"
        # find chucks with numpy vectors to get similier words checked
        similarity_score = score_job_vs_cv(cv_chunks, website_info["content"])
        if similarity_score > 0.7:
            LOG.info(f"Job {job['job_id']} is a strong match!")
        elif similarity_score > 0.5:
            LOG.info(f"Job {job['job_id']} is a moderate match")
        else:
            LOG.info(f"Job {job['job_id']} is a weak match")
        google_sheet_data["rating_vs_cv"] = round(similarity_score * 100, 2)

        if similarity_score > 0.5:
            start = datetime.datetime.now()
            # Initialize the JobRanker once, probably at the top of rate_job_posts
            ranker = JobRanker(model, tokenizer)

            all_scores = []
            all_missing_skills = []
            all_justifications = []
            for cv_chunk in cv_chunks:
                # Pass the CV and job description to the LLM
                llm_result = ranker.rate_job_chunk(
                    cv_text=cv_chunk,
                    job_text=website_info["content"],
                    max_new_tokens=150,  # optional: adjust length
                    temperature=0.1,  # optional: low temp for more deterministic scoring
                )
                all_scores.append(llm_result["score"])
                all_missing_skills.extend(llm_result.get("missing_skills", []))
                justification = llm_result.get("justification")
                if justification:
                    all_justifications.append(justification)
            # remove duplicate skills
            all_missing_skills = list(set(all_missing_skills))

            # Combine into one paragraph
            combined_justification = " ".join(all_justifications)

            # Aggregate results, e.g., take max or average
            final_score = max(all_scores)
            end = datetime.datetime.now()
            elapsed = end - start
            total_seconds = int(elapsed.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            LOG.info("Finished running LLM check.")
            LOG.info(f"Elapsed time: {hours}h {minutes}m {seconds}s")
            LOG.info(f"Aggregated LLM score: {final_score}")
            LOG.info(f"Missing skills from job description: {all_missing_skills}")
            LOG.info(f"Justification: {combined_justification}")
        break

    #TODO upload the results to the google sheet tab "rated_jobs"

if __name__ == '__main__':
    from pprint import pprint
    job_links = [
        {
            "company": "AyZar Outreach",
            "job_id": "80be68f6e59b50be808ca108e0c64f7c965f71db042245fb89afc9d6bd2e75af",
            "jog_title": "Animator",
            "link": "https://www.linkedin.com/jobs/view/animator-at-ayzar-outreach-4360896392",
            "location": "California, United States",
        },
        {
            "company": "Framestore",
            "job_id": "ba4a50093e5f7da915094d3f7e307adaec668f1300ca55af3ec2403f17fc7a1b",
            "jog_title": "3D Animator",
            "link": "https://framestore.recruitee.com/o/animateurtrice-3d-3d-animator-3",
            "location": "Montreal, Quebec, Canada",
        },
    ]

    pdf_file_path = r"D:\storage\documents\job_hunting\Mark Conrad - Resume - Animation.pdf"
    json_token_path = r"D:\storage\programming\python\job_scanner\credentials\open_ai_api_key.json"
    rate_job_posts(job_links,pdf_file_path, json_token_path)