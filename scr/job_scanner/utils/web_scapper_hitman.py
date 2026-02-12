import time
import random
from job_scanner.utils.logger_setup import start_logger
from job_scanner.utils.webpage_scrapping_utils import access_json_api, job_id_from_url


LOG = start_logger()

def scrape_hitmarker_jobs(
    keyword: str,
    pages: int = 3,
    pull_min_time: float = 1.5,
    pull_max_time: float = 3.0,
    base_url: str = "https://hitmarker.net/api/jobs",
    job_ids_used:set[str] = set(),
) -> list[dict]:
    """
    Scrapes job listings from Hitmarker based on the provided keyword and number of pages.

    Args:
        keyword (str): The search keyword for job listings.
        pages (int): The number of pages to scrape. Default is 3.
        pull_min_time (float): Minimum time to wait between requests in seconds. Default is 1.5.
        pull_max_time (float): Maximum time to wait between requests in seconds. Default is 3.0.
        base_url (str): The base URL for the Hitmarker API. Default is "https://hitmarker.net/api/jobs".
        job_ids_used (set[str]): A set of job IDs that have already been processed to avoid duplicates.

    Returns:
        list[dict]: A list of dictionaries, each representing a job listing with details such as job ID,
                    title, company, location, URL, snippet, source, and processed status.
    """

    jobs = []

    for page in range(1, pages + 1):
        params = {
            "search": keyword,
            "page": page,
        }

        response = access_json_api(
            url=base_url,
            params=params
        )
        pprint(response)

        if not response or response.status_code != 200:
            LOG.warning("Hitmarker request blocked or failed")
            break

        data = response.json()
        job_list = data.get("data", [])

        if not job_list:
            LOG.info("No more Hitmarker jobs found.")
            break

        LOG.debug(f"Scraped {len(job_list)} Hitmarker jobs on page {page}")

        for job in job_list:
            job_url = f"https://hitmarker.net/jobs/{job['slug']}"
            job_id = job_id_from_url(job_url)

            if job_id in job_ids_used:
                LOG.info(
                    f"Job already exists in Google Sheet. Skipping Job: {job.get("title", "")} at {job.get("company", {}).get("name", "")}"
                )
                continue
            job_ids_used.add(job_id)

            job_card = {
                "job_id": job_id,
                "title": job.get("title", ""),
                "company": job.get("company", {}).get("name", ""),
                "location": job.get("location", ""),
                "url": job_url,
                "snippet": "",
                "source": "Hitmarker",
                "processed": "No",
            }

            jobs.append(job_card)
            LOG.info(f"Added Hitmarker Job: {job_card['title']}")

        sleep_time = random.uniform(pull_min_time, pull_max_time)
        LOG.debug(f"Sleeping {sleep_time:.2f}s")
        time.sleep(sleep_time)

    LOG.info(f"Finished scraping Hitmarker — total jobs: {len(jobs)}")
    return jobs


if __name__ == "__main__":
    from pprint import pprint

    #TODO need to get this scrapper working currently this will not work with the setup I have
    # look for another way to get the data this may be hidden behind a different system
    jobs = scrape_hitmarker_jobs(keyword="developer", pages=2)
    pprint(jobs)