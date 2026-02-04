import random
import requests
import hashlib
import string
import secrets
import os
from urllib.parse import urlparse, parse_qsl, urlunparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from job_scanner.data.job_lookup_data import job_lookup_data
from job_scanner.utils.logger_setup import start_logger
from typing import Optional


LOG = start_logger()



def random_alphanumeric(length: int = 12) -> str:
    """
    Generate a random alphanumeric string of specified length.

    Args:
        length (int): Length of the generated string.

    Returns:
        random_string (str): Random alphanumeric string.
    """
    alphabet = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(alphabet) for _ in range(length))
    return random_string


def access_json_api(
    url: str,
    params: dict | None = None,
    retry_total: int = 3,
    backoff_time: float = 0.5,
    timeout: int = 10,
) -> Optional[dict]:
    """
    Access a JSON API endpoint safely with retries, headers, and basic bot-avoidance.

    Args:
        url (str): API endpoint URL
        params (dict | None): Query parameters
        retry_total (int): Total retry attempts
        backoff_time (float): Backoff factor between retries
        timeout (int): Request timeout in seconds

    Returns:
        dict | None: Parsed JSON response or None on failure
    """

    session = requests.Session()

    retries = Retry(
        total=retry_total,
        backoff_factor=backoff_time,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    headers = {
        "User-Agent": random.choice(job_lookup_data(2)),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://hitmarker.net/jobs",
        "Connection": "keep-alive",
    }

    proxy_url = os.environ.get("HTTP_PROXY")
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

    try:
        response = session.get(
            url,
            headers=headers,
            params=params,
            timeout=timeout,
            proxies=proxies,
        )

        LOG.debug(f"JSON API response code: {response.status_code}")

        if response.status_code != 200:
            LOG.warning(f"Non-200 response from JSON API: {response.status_code}")
            return None

        return response.json()

    except requests.exceptions.RequestException as e:
        LOG.error(f"JSON API request failed: {e}")
        return None

def access_html_webpage(lined_base_url: str, retry_total: int = 3, backoff_time: float = 0.5, params: dict | None = None) -> Optional[requests.Response]:
    """
    This will access a web page and use random agent to access it
    this is good for HTML based sites not Json sights

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