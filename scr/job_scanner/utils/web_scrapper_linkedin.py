import time
import random
import requests
import hashlib
import os
from job_scanner.utils.logger_setup import start_logger
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qsl, urlunparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from job_scanner.data.job_lookup_data import job_lookup_data
from typing import Optional


LOG = start_logger()

def access_webpage(lined_base_url: str, retry_total: int = 3, backoff_time: float = 0.5, params: dict | None = None) -> Optional[requests.Response]:
    """
    This will access a web page and use random agent to access it

    Args:
        params (dict): the parameter to access from the page
        lined_base_url (str): this is the ural to get access to
        retry_total (int): this is the number of times to attempt to connect
        backoff_time (float): how many seconds to back off from trying to connect again

    Returns:
        response | None (requests.Response): this is the data from the webpage that was rotated
    """
    # create a session with retries
    session = requests.Session()
    retries = Retry(
        total=retry_total,
        backoff_factor=backoff_time,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # rotate user-agent (use your job_lookup_data or a list)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    headers = {
        "User-Agent": random.choice(job_lookup_data(2)),
        "Accept-Language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.8"]),
        "Accept": "text/html,application/xhtml+xml",
        "Connection": random.choice(["keep-alive", "close"]),
    }

    # set a proxy string if needed
    proxy_url = os.environ.get("HTTP_PROXY")  # e.g., "http://username:password@proxy.example:3128"
    proxies_map = {"http": proxy_url, "https": proxy_url} if proxy_url else None

    # perform the request with params, timeout and optional proxies
    response = session.get(
        lined_base_url,
        headers=headers,
        params=params,
        timeout=10,
        proxies=proxies_map,
        allow_redirects=True,
    )
    LOG.debug(f"Accessed the setting and got the following response code {response.status_code}")

    content = (response.text or "").lower()  # check the response code
    if response.status_code == 200 != any(term in content for term in ("captcha","access denied","verify you are a human","unusual traffic",)):
        LOG.debug("200 OK — no proxy needed")
        return response
    elif response.status_code in (429,407, 403, 500, 502, 503, 504):
        LOG.debug("Got Response Code: {response.status_code}")
        LOG.debug("429 Too Many Requests — backoff and/or use a proxy/IP rotation")
        LOG.debug("407 Proxy Authentication Required — your environment requires a proxy")
        LOG.debug("403 Forbidden — try using a proxy, rotate User or Agent, or slow requests")
        LOG.debug("[500, 502, 503, 504] Server error — try retries, backoff, or a proxy")

        response = session.get(
            lined_base_url,
            headers={"User-Agent": random.choice(job_lookup_data(2))},
            params=params,
            timeout=10,
            proxies=proxies_map,
            allow_redirects=True,
        )
        return response
    return None


def normalize_url(url: str) -> bytes:
    parsed = urlparse(url.lower())
    clean_query = [
        (k, v) for k, v in parse_qsl(parsed.query)
        if not k.startswith("utm_")
    ]
    url_normalized = urlunparse(parsed._replace(query="&".join(f"{k}={v}" for k, v in clean_query))).rstrip("/")

    return url_normalized

def job_id_from_url(url: str) -> str:
    normalized = normalize_url(url)
    job_id = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return job_id

def scrape_linkedin_jobs(keyword: str, location: str, work_type: int, post_date: str, job_type: str, pages: int = 2, pull_min_time: float = 1.8, pull_max_time: float = 3.6) -> list[dict]:
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

    Returns:
        list[dict]: List of job listings with title, company, location, url, and source
    """
    lined_base_url = (
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"  # found when you inspect the network activity on linkedin jobs page
    )
    
    jobs = []
    for page in range(pages):
        params = {
            "keywords": keyword,
            "location": location,
            "f_WT": work_type,
            "f_TPR": post_date,
            "start": page * 25,
        }
        response = access_webpage(
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

    """
    jobs = scrape_linkedin_jobs(
        keyword="Animator",
        location="Worldwide",
        work_type=2,
        job_type="F,C",
        post_date= "r2592000",
        pages=2,
    )"""

    job_id = job_id_from_url(r"https://framestore.recruitee.com/o/animateurtrice-3d-3d-animator-3".split("?")[0])
    print(job_id)