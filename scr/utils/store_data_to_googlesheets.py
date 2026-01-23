import datetime
import gspread
from pathlib import Path
import os
from google.oauth2.service_account import Credentials
from job_scanner.scr.utils.logger_setup import start_logger


LOG = start_logger()


def log_google_sheet_data(
        creds_path: str,
        scopes: list,
        google_sheet_url: str,
        data: list,
        tab_name: None | str = None) -> str:
    """
    This will log data to a google sheet

    Args:
        creds_path (str): The path to the service account credentials JSON file
        scopes (list): The list of scopes to use for the authentication
        google_sheet_url (str): The name of the google sheet to update
        data (list): The data to append to the google sheet
        tab_name (str | None): The name of the tab to update, if None, the first tab will be used

    Returns:
        msg (str): The message to log if the action worked out
    """
    client = authenticate_google_sheets(creds_path, scopes)

    update_google_sheet(client, google_sheet_url, data, tab_name)
    msg = f"Google sheet '{google_sheet_url}' updated successfully."


    LOG.info(msg)

    return msg

def authenticate_google_sheets(creds_path: str, scopes: list) -> gspread.Client:
    """
    This will authenticate the google sheets API using a service account

    Args:
        creds_path (str): The path to the service account credentials JSON file
        scopes (list): The list of scopes to use for the authentication

    Returns:
        gspread.Client: The authenticated gspread client
    """
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)

    return gspread.authorize(creds)

def update_google_sheet(
        google_client: gspread.Client,
        google_sheet_url: str,
        data: list,
        tab_name: None | str = None) -> None:
    """
    This will update a google sheet with the job information

    Args:
        google_client (gspread.Client): The authenticated gspread client
        data (list): The data to append to the google sheet
        google_sheet_url (str): The name of the google sheet to update
        tab_name (str | None): The name of the tab to update, if None, the first tab will be used
    """
    print(google_sheet_url)
    spreadsheet = google_client.open_by_url(google_sheet_url)
    if tab_name:
        sheet = spreadsheet.worksheet(tab_name)
    else:
        sheet = spreadsheet.get_worksheet(0)

    # insert a blank for first
    sheet.insert_row([], index=2)

    # add data to the sheet
    sheet.append_rows(data)

if __name__ == '__main__':
    data = [
        {
            "title": "Freelance Animator – Comic",
            "company": "Twine",
            "location": "United States",
            "url": "https://www.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352513393",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Freelance Animator – Comic",
            "company": "Twine",
            "location": "United Kingdom",
            "url": "https://uk.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352593401",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Freelance Animator – Comic",
            "company": "Twine",
            "location": "New Zealand",
            "url": "https://nz.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352543356",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Freelance Animator – Comic",
            "company": "Twine",
            "location": "European Economic Area",
            "url": "https://www.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352653391",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Freelance Animator – Comic",
            "company": "Twine",
            "location": "Australia",
            "url": "https://au.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352563368",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Freelance Animator – Comic",
            "company": "Twine",
            "location": "Canada",
            "url": "https://ca.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352623501",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Freelance Animator – Comic",
            "company": "Twine",
            "location": "Switzerland",
            "url": "https://ch.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352543357",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Freelance Animator – Comic",
            "company": "Twine",
            "location": "Singapore",
            "url": "https://sg.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352633468",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "2D Animator",
            "company": "GamblingCareers.com",
            "location": "Philippines",
            "url": "https://ph.linkedin.com/jobs/view/2d-animator-at-gamblingcareers-com-4362458251",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "2D Animator (Freelance)",
            "company": "HAUS",
            "location": "United States",
            "url": "https://www.linkedin.com/jobs/view/2d-animator-freelance-at-haus-4364057905",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Freelance Animator",
            "company": "Twine",
            "location": "European Economic Area",
            "url": "https://www.linkedin.com/jobs/view/freelance-animator-at-twine-4352563363",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Junior Level Animator",
            "company": "Magic Media",
            "location": "Bucharest, Bucharest, Romania",
            "url": "https://ro.linkedin.com/jobs/view/junior-level-animator-at-magic-media-4346569646",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Junior Level Animator",
            "company": "Magic Media",
            "location": "Porto, Portugal",
            "url": "https://pt.linkedin.com/jobs/view/junior-level-animator-at-magic-media-4346760936",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Animator | Motion Graphics | Work From Home",
            "company": "Cast LMS (Buri Technologies Inc)",
            "location": "Quezon City, National Capital Region, Philippines",
            "url": "https://ph.linkedin.com/jobs/view/animator-motion-graphics-work-from-home-at-cast-lms-buri-technologies-inc-4363852815",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Freelance Animator",
            "company": "Twine",
            "location": "Australia",
            "url": "https://au.linkedin.com/jobs/view/freelance-animator-at-twine-4352504329",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Freelance Animator",
            "company": "Twine",
            "location": "New Zealand",
            "url": "https://nz.linkedin.com/jobs/view/freelance-animator-at-twine-4352543355",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Junior Level Animator",
            "company": "Magic Media",
            "location": "Belgrade, Serbia",
            "url": "https://rs.linkedin.com/jobs/view/junior-level-animator-at-magic-media-4346615300",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Junior Level Animator",
            "company": "Magic Media",
            "location": "Kyiv, Ukraine",
            "url": "https://ua.linkedin.com/jobs/view/junior-level-animator-at-magic-media-4346653548",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Freelance Animator",
            "company": "Twine",
            "location": "Switzerland",
            "url": "https://ch.linkedin.com/jobs/view/freelance-animator-at-twine-4352713426",
            "snippet": "",
            "source": "LinkedIn",
        },
        {
            "title": "Animator",
            "company": "AyZar Outreach",
            "location": "California, United States",
            "url": "https://www.linkedin.com/jobs/view/animator-at-ayzar-outreach-4360896392",
            "snippet": "",
            "source": "LinkedIn",
        },
    ]
    service_account_file = r"D:\storage\programming\python\job_scanner\credentials\jogscrapperproject-0a441d890893.json"

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
    ]

    google_sheet_url = "https://docs.google.com/spreadsheets/d/1D992PCSaAX-L648D26jMa4fSVtMaOIp5Y34TpYY4ajM/edit?gid=0#gid=0"
    jog_data = [[job["title"], job["company"], job["location"], job["url"], job["source"], datetime.datetime.now().strftime("%m/%d/%Y")] for job in data]

    log_google_sheet_data(
        creds_path=service_account_file,
        scopes=scopes,
        google_sheet_url=google_sheet_url,
        data=jog_data,
        tab_name="scraped_data",
    )