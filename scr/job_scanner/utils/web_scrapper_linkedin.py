import time
import random
from job_scanner.utils.logger_setup import start_logger
from bs4 import BeautifulSoup
from job_scanner.utils.webpage_scrapping_utils import access_html_webpage, job_id_from_url


LOG = start_logger()

def scrape_linkedin_jobs(
        keyword: str,
        location: str,
        work_type: int,
        post_date: str,
        job_type: str,
        pages: int = 2,
        pull_min_time: float = 1.8,
        pull_max_time: float = 3.6,
        lined_base_url: str = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search",
) -> list[dict]:
    """
    Scrape LinkedIn job listings based on keyword and location. There are
    some nuances to doing this so I'll put those notes here.

    Args:
        keyword (str): Job title or keywords to search for
        location (str): Location to search for jobs. (e.g., "Worldwide", "United States", "Europe", "Ireland)
        work_type (int): Work type filter (1=On-site, 2=Remote, 3=Hybrid)
        job_type (int): Job type filter (F=Full-time, P=Part-time, C=Contract, T=Temporary, I=Internship, V=Volunteer)
        post_date (str): Date posted filter (e.g., "r86400" for last 24 hours, "r604800" for last 7 days, "r2592000" for last 30 days)
        pages (int): Number of baches of jobs to retrive page*25 (25 jobs per page)
        pull_min_time (float): Minimum time to wait between requests
        pull_max_time (float): Maximum time to wait between requests
        lined_base_url (str): Base URL for LinkedIn job search API

    Returns:
        list[dict]: List of job listings with title, company, location, url, and source
    """
    jobs = []
    for page in range(pages):
        params = {
            "keywords": keyword,
            "location": location,
            "f_WT": work_type,
            "f_TPR": post_date,
            "start": page * 25,
        }
        response = access_html_webpage(
            params=params,
            lined_base_url=lined_base_url
        )
        if not response:
            LOG.warning("LinkedIn blocked request Access we could not scrape anything")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("li")

        if not cards:
            LOG.info("No more jobs returned. Stopping early.")
            break

        LOG.debug(f"Scraped {len(cards)} jobs from LinkedIn on page {page + 1}")

        for card in cards:
            title_el = card.select_one("h3")
            company_el = card.select_one("h4")
            location_el = card.select_one(".job-search-card__location")
            link_el = card.select_one("a")

            if not title_el or not company_el or not link_el:
                continue

            # Snippet from card if exists
            snippet_el = card.select_one("p")
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""

            job_id = job_id_from_url(link_el["href"].split("?")[0])
            job_card = {
                "job_id": job_id,
                "title": title_el.get_text(strip=True),
                "company": company_el.get_text(strip=True),
                "location": location_el.get_text(strip=True) if location_el else "",
                "url": link_el["href"].split("?")[0],
                "snippet": snippet,
                "source": "LinkedIn",
                "processed": "No"
            }

            jobs.append(job_card)
            LOG.info(
                f"Added Job: {title_el.get_text(strip=True)} at {company_el.get_text(strip=True)}"
            )

            sleep_time = random.uniform(1.8, 3.6)

            LOG.debug(f"Sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

    LOG.info(f"Finished Scrapping Linkedin\nTotal jobs scraped from LinkedIn: {len(jobs)}")
    return jobs

if __name__ == "__main__":
    """
    LinkedIn Job Scraper Nuances:
    """
    from pprint import pprint

    jobs = scrape_linkedin_jobs(
        keyword="Animator",
        location="Worldwide",
        work_type=2,
        job_type="F,C",
        post_date= "r2592000",
        pages=2,
    )

    #job_id = job_id_from_url(r"https://framestore.recruitee.com/o/animateurtrice-3d-3d-animator-3".split("?")[0])
    pprint(jobs)