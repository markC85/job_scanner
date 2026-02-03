from job_scanner.utils.web_scrapper_linkedin import scrape_linkedin_jobs
from job_scanner.utils.google_sheet_util import log_google_sheet_data, pull_google_sheet_data
from job_scanner.utils.rate_job_posting import rate_job_posts
from job_scanner.utils.logger_setup import start_logger
import datetime


LOG = start_logger()

"""
This is the tool I am creating to improve my Job search process.
I want to be able to learn more how to use LLM's and AI agents to help
me create better models.

Tool Scope:
- Scrape job postings from various job boards based on user-defined queries.
- Log the scraped job postings into a Google Sheet for easy access and tracking.
- Rate the job postings against a provided resume using an LLM to determine fit.

Things I want to improve on this tool:
"""
# TODO: I want to improve the way the LLM can rate the jobs postings via JSON PARSING.
# TODO: I want to add more job boards to scrape from (Indeed, Glassdoor, etc)
# TODO: I want to train my LLM to parse data correctly from websites so it can auto build the JSON structure.
# TODO: I want to build a system that auto build a resume based on the job description and my experience to keep
# my resume to 1000 words and only have relevant experience for the job I am applying for.

def job_scanner(
        queries: list[tuple[str,str]],
        service_account_file: str,
        scopes: list[str],
        google_sheet_url: str) -> None:
    """
    Main function to run the job scanner tool.
    
    This will scan all the jobs from the different job boards and
    compile them into a Google Sheet for easy access and tracking.
    
    Args:
        queries (list of tuples): List of (keyword, location) pairs to search for jobs.
        service_account_file (str): Path to the Google service account JSON file.
        scopes (list of str): List of Google API scopes required.
        google_sheet_url (str): URL of the Google Sheet to store job listings.
    
    """
    timer_start = datetime.datetime.now()

    linkedin_jobs = scrape_linkedin_jobs(
        queries=queries,
        work_type=2,
        job_type="F,C",
        post_date="r604800",
        pages=2,
        creds_path=service_account_file,
        scopes=scopes,
        google_sheet_url=google_sheet_url,
        tab_name="scraped_data",
    )
    if not linkedin_jobs:
        LOG.info("No new LinkedIn jobs found from linkedin scrape.")
        return

    # log the latest job data to google sheets
    jog_data = [
        [
            job["job_id"],
            job["title"],
            job["company"],
            job["location"],
            job["url"],
            job["source"],
            datetime.datetime.now().strftime("%m/%d/%Y"),
            job["processed"],
        ]
        for job in linkedin_jobs
    ]
    log_google_sheet_data(
        creds_path=service_account_file,
        scopes=scopes,
        google_sheet_url=google_sheet_url,
        data=jog_data,
        tab_name="scraped_data",
    )
    # Calculate elapsed time
    timer_end = datetime.datetime.now()
    elapsed = timer_end - timer_start
    total_seconds = int(elapsed.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    LOG.info(
        f"Logged {len(linkedin_jobs)} total job entries into google sheet from Linkedin."
    )
    LOG.info(f"Elapsed time Tool Ran: {hours}h {minutes}m {seconds}s")

def job_ratter(
        service_account_file: str,
        scopes: list[str],
        google_sheet_url: str,
        pdf_file_path: str,
        json_token_path: str)-> None:
    """
    rate the jobs that have been scrapped and logged to the google sheet

    Args:
        service_account_file (str): Path to the Google service account JSON file.
        scopes (list of str): List of Google API scopes required.
        google_sheet_url (str): URL of the Google Sheet to store job listings.
        pdf_file_path (str): Path to the PDF resume file.
        json_token_path (str): Path to the JSON file containing OpenAI API key.
    """
    timer_start = datetime.datetime.now()

    # pull the data from the Google sheets
    pulled_data = pull_google_sheet_data(
        creds_path=service_account_file,
        scopes=scopes,
        google_sheet_url=google_sheet_url,
        tab_name="scraped_data"
    )

    LOG.info(f"Pulled {len(pulled_data)} total job entries from google sheet.")

    upload_to_google_sheets = rate_job_posts(pulled_data,pdf_file_path, json_token_path)

    jog_data = [
        [
            job["job_id"],
            job["rating_vs_cv"],
            job["missing_skills"],
            job["jog_title"],
            job["company"],
            job["location"],
            job["link"],
            job["date_processed"],
            job["cv_used"],
            job["scraped_failed"],
            job["scraped_failed_error_message"],
            job["no_matching_job_title"],
            job["llm_ranking"],
            job["llm_justification"]
        ]
        for job in upload_to_google_sheets
    ]

    log_google_sheet_data(
        creds_path=service_account_file,
        scopes=scopes,
        google_sheet_url=google_sheet_url,
        data=jog_data,
        tab_name="processed_jobs",
    )
    # Calculate elapsed time
    timer_end = datetime.datetime.now()
    elapsed = timer_end - timer_start
    total_seconds = int(elapsed.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    LOG.info(
        f"Logged {len(jog_data)} jobs from the LLM processing onto the processed_jobs tab in job_scraper sheet."
    )
    LOG.info(f"Elapsed time Tool Ran: {hours}h {minutes}m {seconds}s")