import datetime
import gspread
from google.oauth2.service_account import Credentials
from job_scanner.utils.logger_setup import start_logger


LOG = start_logger()

def pull_google_sheet_data(
        creds_path: str,
        scopes: list,
        google_sheet_url: str,
        tab_name: None | str = None) -> list:
    """
    This will pull the google data sheet information

    Args:
        creds_path (str): The path to the service account credentials JSON file
        scopes (list): The list of scopes to use for the authentication
        google_sheet_url (str): The name of the google sheet to update
        tab_name (str | None): The name of the tab to update, if None, the first tab will be used
    """
    google_client = authenticate_google_sheets(creds_path, scopes)
    spreadsheet = google_client.open_by_url(google_sheet_url)

    if tab_name:
        sheet = spreadsheet.worksheet(tab_name)
    else:
        sheet = spreadsheet.get_worksheet(0)

    # get all the data
    all_data = sheet.get_all_records()
    html_links = []
    for idx, row in enumerate(all_data, start=2):  # start=2 because row 1 is headers
        if row.get("Processed", "").strip().lower() != "yes":
            # Your processing here
            LOG.debug(f"Processing row:{row}")
            html_links.append(
                {
                    "job_id": row.get("Job ID"),
                    "link": row.get("Link"),
                    "jog_title": row.get("Job Title"),
                    "company": row.get("Company"),
                    'location': row.get("Location")
                }
            )

            # Update the 'Processed' column to 'Yes'
            sheet.update_cell(idx, list(row.keys()).index("Processed") + 1, "Yes")

    return html_links


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
    from pprint import pprint
    data = [
    {'company': 'Twine',
      'job_id': '44763387acc3885356e7f2783e823a705ab6137f062e188e88cc443d70b32d39',
      'location': 'United States',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Freelance Animator – Comic',
      'url': 'https://www.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352513393'},
     {'company': 'Twine',
      'job_id': '38dc3706dc8eeff85464f3f6a87f579415a96415d3bc6b628815bf5c45b2587c',
      'location': 'United Kingdom',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Freelance Animator – Comic',
      'url': 'https://uk.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352593401'},
     {'company': 'Twine',
      'job_id': 'de165b4eb47c9e71843cb81d840a0bfcce80a814de30f8aed3d7b5f76ed4ea38',
      'location': 'New Zealand',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Freelance Animator – Comic',
      'url': 'https://nz.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352543356'},
     {'company': 'Twine',
      'job_id': '37d3a97b551e5e9bbff7ac9f0b1e26f49f53cabd3e22366b557ed4adf5eb6207',
      'location': 'European Economic Area',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Freelance Animator – Comic',
      'url': 'https://www.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352653391'},
     {'company': 'Twine',
      'job_id': '6504bc75437f8a0c154a0578170ea7cb05804a9f11762556d2af108e0a0f3171',
      'location': 'Australia',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Freelance Animator – Comic',
      'url': 'https://au.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352563368'},
     {'company': 'Twine',
      'job_id': 'dd3b303f9f7544f9769741c042a4352aa71f60a93803d870489f4d8bc00840d0',
      'location': 'Canada',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Freelance Animator – Comic',
      'url': 'https://ca.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352623501'},
     {'company': 'Twine',
      'job_id': 'a7b6f82b0f8a64baef5d4eccdb75a37833713b60cc4dcec472d0c1873b6cef5e',
      'location': 'Switzerland',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Freelance Animator – Comic',
      'url': 'https://ch.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352543357'},
     {'company': 'Twine',
      'job_id': '79f42d657df347a878a3705acf01871ed8090a1b889671b63800e95936394525',
      'location': 'Singapore',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Freelance Animator – Comic',
      'url': 'https://sg.linkedin.com/jobs/view/freelance-animator-%E2%80%93-comic-at-twine-4352633468'},
     {'company': 'GamblingCareers.com',
      'job_id': '133681732768214ab3d8a298695637e655c78e94baf961b769a07cef43971544',
      'location': 'Philippines',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': '2D Animator',
      'url': 'https://ph.linkedin.com/jobs/view/2d-animator-at-gamblingcareers-com-4362458251'},
     {'company': 'HAUS',
      'job_id': '6d14a4dcd8470692764372dd999e9c512e5e6bab7aa2e0f32b7b9ea506da981e',
      'location': 'United States',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': '2D Animator (Freelance)',
      'url': 'https://www.linkedin.com/jobs/view/2d-animator-freelance-at-haus-4364057905'},
     {'company': 'Twine',
      'job_id': '819cf6993a6056e655c03b3faf9eaa95b733457a4968448036d14358ef8ecc43',
      'location': 'European Economic Area',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Freelance Animator',
      'url': 'https://www.linkedin.com/jobs/view/freelance-animator-at-twine-4352563363'},
     {'company': 'Magic Media',
      'job_id': 'a10393abec6599fefdd7fce9e6560e3a1612281bd653c8804bd08c82612e2138',
      'location': 'Bucharest, Bucharest, Romania',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Junior Level Animator',
      'url': 'https://ro.linkedin.com/jobs/view/junior-level-animator-at-magic-media-4346569646'},
     {'company': 'Magic Media',
      'job_id': '87179176128a09761c109f6921a2a3c05f10736a54ae2c5d8e4a135b6fe29d78',
      'location': 'Porto, Portugal',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Junior Level Animator',
      'url': 'https://pt.linkedin.com/jobs/view/junior-level-animator-at-magic-media-4346760936'},
     {'company': 'Cast LMS (Buri Technologies Inc)',
      'job_id': 'cc6c39d44d16284ef915f48924925aab2622d616968f07ad665d89c3a41e2fb0',
      'location': 'Quezon City, National Capital Region, Philippines',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Animator | Motion Graphics | Work From Home',
      'url': 'https://ph.linkedin.com/jobs/view/animator-motion-graphics-work-from-home-at-cast-lms-buri-technologies-inc-4363852815'},
     {'company': 'Twine',
      'job_id': '3fe23f5617b65448502705ab1406d09b9ed9e2ccf3e26dbb0df2c8ed59f73e40',
      'location': 'Australia',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Freelance Animator',
      'url': 'https://au.linkedin.com/jobs/view/freelance-animator-at-twine-4352504329'},
     {'company': 'Twine',
      'job_id': '56f7db2ea844bd216aaf18c47cae20de8683c7a2309fe193935dc6fe4bca70e1',
      'location': 'New Zealand',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Freelance Animator',
      'url': 'https://nz.linkedin.com/jobs/view/freelance-animator-at-twine-4352543355'},
     {'company': 'Magic Media',
      'job_id': '06f4624642588bb5119499af835c34e5931f9dc16af07a5aa0674e2968a0c7d8',
      'location': 'Belgrade, Serbia',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Junior Level Animator',
      'url': 'https://rs.linkedin.com/jobs/view/junior-level-animator-at-magic-media-4346615300'},
     {'company': 'Magic Media',
      'job_id': 'b91446f77732ac712887e29b3f583e0a47235f28a2f74521f61d85077e35ef8d',
      'location': 'Kyiv, Ukraine',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Junior Level Animator',
      'url': 'https://ua.linkedin.com/jobs/view/junior-level-animator-at-magic-media-4346653548'},
     {'company': 'Twine',
      'job_id': '71472b2c159cc4824ed7219a766830cd5f764c05eec4b36858d7ee9f7bac7026',
      'location': 'Switzerland',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Freelance Animator',
      'url': 'https://ch.linkedin.com/jobs/view/freelance-animator-at-twine-4352713426'},
     {'company': 'AyZar Outreach',
      'job_id': '80be68f6e59b50be808ca108e0c64f7c965f71db042245fb89afc9d6bd2e75af',
      'location': 'California, United States',
      'processed': 'No',
      'snippet': '',
      'source': 'LinkedIn',
      'title': 'Animator',
      'url': 'https://www.linkedin.com/jobs/view/animator-at-ayzar-outreach-4360896392'}
            ]

    service_account_file = r"D:\storage\programming\python\job_scanner\credentials\jogscrapperproject-0a441d890893.json"

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
    ]

    google_sheet_url = "https://docs.google.com/spreadsheets/d/1D992PCSaAX-L648D26jMa4fSVtMaOIp5Y34TpYY4ajM/edit?gid=0#gid=0"
    jog_data = [[job['job_id'], job["title"], job["company"], job["location"], job["url"], job["source"], datetime.datetime.now().strftime("%m/%d/%Y"), job['processed']] for job in data]

    """log_google_sheet_data(
        creds_path=service_account_file,
        scopes=scopes,
        google_sheet_url=google_sheet_url,
        data=jog_data,
        tab_name="scraped_data",
    )"""

    result = pull_google_sheet_data(
        creds_path=service_account_file,
        scopes=scopes,
        google_sheet_url=google_sheet_url,
        tab_name="scraped_data"
    )

    pprint(result)