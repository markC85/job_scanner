import gspread
from google.oauth2.service_account import Credentials
from job_scanner.utils.logger_setup import start_logger
from pprint import pprint


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

def pull_all_job_ids_from_google_sheet(
        creds_path: str,
        scopes: list,
        google_sheet_url: str,
        tab_name: None | str = None) -> list:
    """
    This will pull all the job IDs from a google sheet

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
    job_ids = []
    for _, row in enumerate(all_data, start=2):  # start=2 because row 1 is headers
        # Your processing here
        LOG.debug(f"Processing row:{row}")
        job_ids.append(row.get("Job ID"))

    return job_ids


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
        data (list): The data to append to the google sheet. Must be list of lists: [[row1], [row2], ...]
        google_sheet_url (str): The name of the google sheet to update
        tab_name (str | None): The name of the tab to update, if None, the first tab will be used
    """
    if not data or len(data) == 0:
        LOG.warning("No data to append to Google Sheet")
        return None

    spreadsheet = google_client.open_by_url(google_sheet_url)
    if tab_name:
        sheet = spreadsheet.worksheet(tab_name)
    else:
        sheet = spreadsheet.get_worksheet(0)

    try:
        # For large datasets, it's more reliable to append rows
        # sheet.append_rows() handles multiple rows in one API call
        sheet.append_rows(data)
        LOG.info(f"Successfully appended {len(data)} rows to Google Sheet")
        LOG.debug(f"Data appended to Google Sheet:\n {pprint(data)}")
    except Exception as e:
        LOG.error(f"Error appending rows: {str(e)}")
        # Fallback: append rows in smaller batches
        batch_size = 10
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            try:
                sheet.append_rows(batch)
                LOG.info(f"Appended batch {i//batch_size + 1} ({len(batch)} rows)")
            except Exception as batch_error:
                LOG.error(f"Error appending batch {i//batch_size + 1}: {str(batch_error)}")
                # Final fallback: append one row at a time
                for row in batch:
                    try:
                        sheet.append_row(row)
                    except Exception as row_error:
                        LOG.error(f"Error appending single row: {str(row_error)}")
