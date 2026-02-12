from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional
from pprint import pprint
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from job_scanner.utils.webpage_scrapping_utils import job_id_from_url
from job_scanner.utils.logger_setup import start_logger
from job_scanner.models.sheet_job_record import SheetJobRecord


LOG = start_logger()

def _clean_text(s: str) -> str:
    """
    Normalize whitespace in text: collapse multiple spaces/newlines into single space, and trim.

    Args:
        s: The input string to clean.

    Returns:
        clean_string (str): A cleaned version of the input string with normalized whitespace.
    """
    clean_string = re.sub(r"\s+", " ", s).strip()
    return clean_string


def _job_to_sheet_row(job: SheetJobRecord) -> dict:
    """
    Convert internal SheetJobRecord dataclass -> Google Sheets row dict.

    Args:
        job (SheetJobRecord): SheetJobRecord instance containing job details.

    Returns:
        google_dict (dict): A dictionary mapping Google Sheets column names to job details, ready for insertion into the sheet.
    """
    google_dict = {
        "job_id": job.job_id or "",
        "title": job.title or "",
        "company": job.company or "",
        "location": job.location or "",
        "job_url": job.job_url,
        "source": "gamejobs.co",
        "date_scraped": job.date_scraped or "",
    }
    return google_dict


def _extract_list_row_fields(job_a, job_href_re) -> tuple[str, Optional[str], Optional[str], Optional[str]]:
    """
    Attempts to infer company/location/posted from nearby text on the listing page.
    This is heuristic, but works with the current GameJobs layout most of the time.

    Args:
        job_a: The anchor element corresponding to the job listing title.
        job_href_re: Compiled regex to identify job listing links, used to know when we've

    Returns:
        (tuple) A tuple of (title, company, location, posted) where title is a string
                and company/location/posted may be None if not found.
    """
    # Example text on listing: "3 days ago", "12 hours ago"
    posted_re = re.compile(
        r"\b(\d+)\s+(minute|hour|day|week|month|year)s?\s+ago\b", re.IGNORECASE
    )

    title = _clean_text(job_a.get_text(" ", strip=True))
    company = None
    location = None
    posted = None

    found_company = False
    found_location = False

    steps = 0
    for el in job_a.next_elements:
        steps += 1
        if steps > 220:
            break

        # Stop if we hit the next job anchor in the listing
        if getattr(el, "name", None) == "a" and el is not job_a and el.get("href"):
            href = el["href"].strip()
            if job_href_re.match(href):
                break

        # Company/location are often anchors after the title anchor
        if getattr(el, "name", None) == "a":
            txt = _clean_text(el.get_text(" ", strip=True))
            if not txt or txt.lower() in {"save", "filter", "login", "register"}:
                continue

            if not found_company:
                company = txt
                found_company = True
                continue

            if found_company and not found_location:
                location = txt
                found_location = True
                continue

        # Posted string appears as text like "3 days ago"
        if posted is None:
            txt = None
            if isinstance(el, str):
                txt = _clean_text(el)
            elif getattr(el, "get_text", None):
                txt = _clean_text(el.get_text(" ", strip=True))

            if txt:
                m = posted_re.search(txt)
                if m:
                    posted = m.group(0)

        if found_company and found_location and posted:
            break

    return title, company, location, posted

def _wait_for_job_list(page) -> None:
    """
    Wait for job-like links to appear; helps with protection/interstitials.

    Args:
        page: The Playwright page object to wait on.
    """
    try:
        page.wait_for_selector("a[href*='-at-']", timeout=15_000)
    except Exception:
        pass


def scrape_gamejobs(
    job_title_keywords: list,
    base_url: str = "https://gamejobs.co/search",
    limit: int = 200,
    headless: bool = False,
    job_ids_used:set[str] = set(),
) -> list[dict]:
    """
    Scrape GameJobs.co for animator job listings.

    Args:
        job_title_keywords (list): List of keywords to filter job titles
                  (e.g., ["animator", "technical artist"]). Only listings with
                   at least one of these keywords as a whole word in the title
                   will be included. This allows for more flexible filtering
                   (e.g., including both "animator" and "technical artist" roles)
                   while still ensuring relevance.

        base_url (str): URL to scrape; can include query params for date filtering
                  (e.g. "?a=7d" for past 7 days). details: Whether to visit each
                  job detail page to extract apply_url and description (slower).
                  limit: Max number of animator jobs to return. headless: Whether
                  to run the browser in headless mode (no UI). delay_s: Seconds to
                  wait between requests when fetching job details (to be polite).

        limit (int): This parameter sets an upper bound on the number of animator job
               listings to return. Since the scraper filters for "animator" in the
               job title, it may encounter many listings that do not match this criterion.
               Setting a reasonable limit helps ensure that the scraper completes in a
               timely manner and does not overload the target website with too many requests.

        headless (bool): Running the browser in headless mode means that it will operate without
                  opening a visible window. This is useful for running the scraper on
                  servers or in automated environments where a UI is not needed. However,
                  during development or debugging, it can be helpful to see the browser
                  actions, so setting headless to False allows you to watch the scraping
                  process in real time.

        job_ids_used (set[str]): A set of job ID hashes that have already been seen and added
                   to the Google Sheet.This is used to avoid adding duplicate job listings to
                   the sheet. When the scraper encounters a job listing, it will extract the job
                   ID from the URL and check if it is in this set. If it is, the scraper will skip
                   that listing, ensuring that only new and unique jobs are added to the Google Sheet.
                   This is particularly important for websites like GameJobs.co, where the same job may
                   appear multiple times in different searches or over time.
    Returns:
        (list[dict]): list of dicts matching your Google Sheets schema, filtered to animator titles only.
    """
    scraped_at = datetime.now(timezone.utc).isoformat()

    # Heuristic: GameJobs job detail pages commonly include "-at-" in the slug
    job_href_re = re.compile(r"^/[^?#]*-at-[^?#]+", re.IGNORECASE)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="en-US",
        )
        page = context.new_page()

        page.goto(base_url, wait_until="domcontentloaded")
        _wait_for_job_list(page)

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        jobs: list[SheetJobRecord] = []

        keyword_patterns = [
            re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in job_title_keywords
        ]
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()

            # skip non-job links first
            if not job_href_re.match(href):
                LOG.debug(f"Skipping non-job link with href: {href}")
                continue

            # skip if none of the keywords appear in the href
            if not any(p.search(href) for p in keyword_patterns):
                LOG.debug(f"Skipping job link that does not match keywords. href: {href}")
                continue

            title, company, location, posted = _extract_list_row_fields(a, job_href_re)

            job_url = urljoin(base_url, href)
            job_id = job_id_from_url(job_url)
            if job_id in job_ids_used:
                LOG.info(
                    f"Job already exists in Google Sheet. Skipping Job: {title} at {company}"
                )
                continue
            job_ids_used.add(job_id)

            job = SheetJobRecord(
                source="gamejobs.com",
                scraped_at_utc=scraped_at,
                title=title,
                company=company,
                location=location,
                posted=posted,
                job_url=job_url,
                job_id=job_id,
                date_scraped= datetime.now().strftime("%m/%d/%Y"),
            )

            jobs.append(job)
            if len(jobs) >= limit:
                break

        browser.close()

    rows = [_job_to_sheet_row(j) for j in jobs]

    LOG.info(f"Scraped {len(rows)} total jobs from GameJobs.co with keywords {job_title_keywords}.")
    LOG.debug(f"Found the following jobs: \n{pprint(rows)}")
    return rows