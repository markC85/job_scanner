import datetime
import trafilatura
import re
from job_scanner.utils.logger_setup import start_logger
from job_scanner.utils.web_scrapper_linkedin import access_webpage
from job_scanner.data.job_lookup_data import job_lookup_data
from bs4 import BeautifulSoup
from typing import Optional

LOG = start_logger()


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

def scrape_pdf_file():
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
    pprint(job_title)
    if not any(kw in text for kw in keywords_include) and not any(kw in job_title for kw in keywords_include):
        LOG.debug("We did not find any for the keywords_include in the text")
        return False
    if any(kw in text for kw in keywords_exclude):
        return False
    return True

def rate_job_posts(job_links: list, cv_file_path: str):
    """
    This will rate all the job links that are passed comparing them to a cv to see
    if there close to what you do and looking for keywords

    Args:
        job_links (list): this is the jobs
        cv_file_path (str): a path to the pdf file that is your CV
    """
    upload_to_google_sheets = []
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
            "cv_used": str(cv_file_path),
            "scraped_failed": 'No',
            "no_matching_job_title": ''
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
            LOG.debug("The job description either did not have the job title I am looking for or had one of ignore words in it")
            google_sheet_data['no_matching_job_title']='Yes'
            upload_to_google_sheets.append(google_sheet_data)
            continue
        website_info['jog_id']=job['job_id']
        pprint(website_info)

        #TODO break down the pdf file that is my cv into a str that the LLM can understand

        #TODO use the cv_data and the link_data and compare them with a LLM
        break

    #TODO upload the results to the google sheet tab "rated_jobs"

if __name__ == '__main__':
    from pprint import pprint
    job_links = [
        {
            "company": "Twine",
            "job_id": "44763387acc3885356e7f2783e823a705ab6137f062e188e88cc443d70b32d39",
            "jog_title": "Freelance Animator – Comic",
            "link": "https://www.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352513393",
            "location": "United States",
        },
        {
            "company": "Twine",
            "job_id": "38dc3706dc8eeff85464f3f6a87f579415a96415d3bc6b628815bf5c45b2587c",
            "jog_title": "Freelance Animator – Comic",
            "link": "https://uk.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352593401",
            "location": "United Kingdom",
        },
        {
            "company": "Twine",
            "job_id": "de165b4eb47c9e71843cb81d840a0bfcce80a814de30f8aed3d7b5f76ed4ea38",
            "jog_title": "Freelance Animator – Comic",
            "link": "https://nz.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352543356",
            "location": "New Zealand",
        },
        {
            "company": "Twine",
            "job_id": "37d3a97b551e5e9bbff7ac9f0b1e26f49f53cabd3e22366b557ed4adf5eb6207",
            "jog_title": "Freelance Animator – Comic",
            "link": "https://www.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352653391",
            "location": "European Economic Area",
        },
        {
            "company": "Twine",
            "job_id": "6504bc75437f8a0c154a0578170ea7cb05804a9f11762556d2af108e0a0f3171",
            "jog_title": "Freelance Animator – Comic",
            "link": "https://au.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352563368",
            "location": "Australia",
        },
        {
            "company": "Twine",
            "job_id": "dd3b303f9f7544f9769741c042a4352aa71f60a93803d870489f4d8bc00840d0",
            "jog_title": "Freelance Animator – Comic",
            "link": "https://ca.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352623501",
            "location": "Canada",
        },
        {
            "company": "Twine",
            "job_id": "a7b6f82b0f8a64baef5d4eccdb75a37833713b60cc4dcec472d0c1873b6cef5e",
            "jog_title": "Freelance Animator – Comic",
            "link": "https://ch.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352543357",
            "location": "Switzerland",
        },
        {
            "company": "Twine",
            "job_id": "79f42d657df347a878a3705acf01871ed8090a1b889671b63800e95936394525",
            "jog_title": "Freelance Animator – Comic",
            "link": "https://sg.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352633468",
            "location": "Singapore",
        },
        {
            "company": "GamblingCareers.com",
            "job_id": "133681732768214ab3d8a298695637e655c78e94baf961b769a07cef43971544",
            "jog_title": "2D Animator",
            "link": "https://ph.linkedin.com/jobs/view/2d-animator-at-gamblingcareers-com-4362458251",
            "location": "Philippines",
        },
        {
            "company": "HAUS",
            "job_id": "6d14a4dcd8470692764372dd999e9c512e5e6bab7aa2e0f32b7b9ea506da981e",
            "jog_title": "2D Animator (Freelance)",
            "link": "https://www.linkedin.com/jobs/view/2d-animator-freelance-at-haus-4364057905",
            "location": "United States",
        },
        {
            "company": "Twine",
            "job_id": "819cf6993a6056e655c03b3faf9eaa95b733457a4968448036d14358ef8ecc43",
            "jog_title": "Freelance Animator",
            "link": "https://www.linkedin.com/jobs/view/freelance-animator-at-twine-4352563363",
            "location": "European Economic Area",
        },
        {
            "company": "Magic Media",
            "job_id": "a10393abec6599fefdd7fce9e6560e3a1612281bd653c8804bd08c82612e2138",
            "jog_title": "Junior Level Animator",
            "link": "https://ro.linkedin.com/jobs/view/junior-level-animator-at-magic-media-4346569646",
            "location": "Bucharest, Bucharest, Romania",
        },
        {
            "company": "Magic Media",
            "job_id": "87179176128a09761c109f6921a2a3c05f10736a54ae2c5d8e4a135b6fe29d78",
            "jog_title": "Junior Level Animator",
            "link": "https://pt.linkedin.com/jobs/view/junior-level-animator-at-magic-media-4346760936",
            "location": "Porto, Portugal",
        },
        {
            "company": "Cast LMS (Buri Technologies Inc)",
            "job_id": "cc6c39d44d16284ef915f48924925aab2622d616968f07ad665d89c3a41e2fb0",
            "jog_title": "Animator | Motion Graphics | Work From Home",
            "link": "https://ph.linkedin.com/jobs/view/animator-motion-graphics-work-from-home-at-cast-lms-buri-technologies-inc-4363852815",
            "location": "Quezon City, National Capital Region, Philippines",
        },
        {
            "company": "Twine",
            "job_id": "3fe23f5617b65448502705ab1406d09b9ed9e2ccf3e26dbb0df2c8ed59f73e40",
            "jog_title": "Freelance Animator",
            "link": "https://au.linkedin.com/jobs/view/freelance-animator-at-twine-4352504329",
            "location": "Australia",
        },
        {
            "company": "Twine",
            "job_id": "56f7db2ea844bd216aaf18c47cae20de8683c7a2309fe193935dc6fe4bca70e1",
            "jog_title": "Freelance Animator",
            "link": "https://nz.linkedin.com/jobs/view/freelance-animator-at-twine-4352543355",
            "location": "New Zealand",
        },
        {
            "company": "Magic Media",
            "job_id": "06f4624642588bb5119499af835c34e5931f9dc16af07a5aa0674e2968a0c7d8",
            "jog_title": "Junior Level Animator",
            "link": "https://rs.linkedin.com/jobs/view/junior-level-animator-at-magic-media-4346615300",
            "location": "Belgrade, Serbia",
        },
        {
            "company": "Magic Media",
            "job_id": "b91446f77732ac712887e29b3f583e0a47235f28a2f74521f61d85077e35ef8d",
            "jog_title": "Junior Level Animator",
            "link": "https://ua.linkedin.com/jobs/view/junior-level-animator-at-magic-media-4346653548",
            "location": "Kyiv, Ukraine",
        },
        {
            "company": "Twine",
            "job_id": "71472b2c159cc4824ed7219a766830cd5f764c05eec4b36858d7ee9f7bac7026",
            "jog_title": "Freelance Animator",
            "link": "https://ch.linkedin.com/jobs/view/freelance-animator-at-twine-4352713426",
            "location": "Switzerland",
        },
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

    job_links = [
        {
            "company": "Framestore",
            "job_id": "ba4a50093e5f7da915094d3f7e307adaec668f1300ca55af3ec2403f17fc7a1b",
            "jog_title": "3D Animator",
            "link": "https://framestore.recruitee.com/o/animateurtrice-3d-3d-animator-3",
            "location": "Montreal, Quebec, Canada",
        }
    ]

    cv_file_path = r"D:\storage\documents\job_hunting\Mark Conrad - Resume - Animation.pdf"
    rate_job_posts(job_links,cv_file_path)