from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional
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
    base_url: str = "https://gamejobs.co/search",
    limit: int = 200,
    headless: bool = False,
    job_ids_used:set[str] = set(),
) -> list[dict]:
    """
    Scrape GameJobs.co for animator job listings.

    Args:
        base_url: URL to scrape; can include query params for date filtering
                  (e.g. "?a=7d" for past 7 days). details: Whether to visit each
                  job detail page to extract apply_url and description (slower).
                  limit: Max number of animator jobs to return. headless: Whether
                  to run the browser in headless mode (no UI). delay_s: Seconds to
                  wait between requests when fetching job details (to be polite).
        detail: If True, the scraper will visit each individual job listing page
                to extract additional details like the application URL and job
                description. This can provide richer data but will significantly
                increase the time taken to complete the scraping process, especially
                if there are many listings. If False, the scraper will only extract
                information available on the listing page, which is faster but may
                miss some details.
        limit: This parameter sets an upper bound on the number of animator job
               listings to return. Since the scraper filters for "animator" in the
               job title, it may encounter many listings that do not match this criterion.
               Setting a reasonable limit helps ensure that the scraper completes in a
               timely manner and does not overload the target website with too many requests.
        headless: Running the browser in headless mode means that it will operate without
                  opening a visible window. This is useful for running the scraper on
                  servers or in automated environments where a UI is not needed. However,
                  during development or debugging, it can be helpful to see the browser
                  actions, so setting headless to False allows you to watch the scraping
                  process in real time.
        delay_s: When fetching details from individual job pages, it's important to be
                 polite and avoid sending too many requests in a short period of time,
                 which can lead to being blocked by the website. The delay_s parameter
                 allows you to specify how many seconds to wait between requests when
                 visiting job detail pages. A delay of around 0.5 to 1 second is often
                 recommended for web scraping to balance speed and politeness.
    Returns:
        (list[dict]): list of dicts matching your Google Sheets schema, filtered to animator titles only.
    """
    scraped_at = datetime.now(timezone.utc).isoformat()

    # Filter: ONLY keep job titles containing "animator" as a whole word (case-insensitive)
    animator_title_re = re.compile(r"\banimator\b", re.IGNORECASE)

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

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not job_href_re.match(href):
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

            # FILTER: only keep "animator" in job title
            if not title or not animator_title_re.search(title):
                continue

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
    return rows