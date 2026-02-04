import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QDialog,
    QFormLayout,
    QPlainTextEdit,
    QMessageBox
)
from job_scanner.utils.google_sheet_util import update_google_sheet, authenticate_google_sheets
from job_scanner.utils.webpage_scrapping_utils import job_id_from_url, random_alphanumeric
from pprint import pprint


class ManuallyEnteredDataUI(QDialog):
    """
    UI for manually entering job data into the
    application to be sent to Google Sheets.
    """
    def __init__(self, version: str, parent=None, google_url: str | None = None, creds_path: str | None = None, scopes: list | None = None):
        super().__init__(parent)

        self.google_url_line_edit = google_url if google_url else ""
        self.creds_path = creds_path if creds_path else ""
        self.scopes = scopes if scopes else []
        self._ui_widgets(version)
        self._create_connections()

    def _ui_widgets(self,version):
        """
        UI fields and layout
        """
        self.setWindowTitle(f"Manually Entered Data v{version}")
        self.resize(430, 400)

        main_layout = QVBoxLayout(self)

        # Scroll area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        linkedin_layout = QFormLayout(content_widget)
        linkedin_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.job_title_input = QLineEdit()
        linkedin_layout.addRow("Job Title:", self.job_title_input)
        self.company_input = QLineEdit()
        linkedin_layout.addRow("Company:", self.company_input)
        self.location_input = QLineEdit()
        linkedin_layout.addRow("Location:", self.location_input)
        self.link_input = QLineEdit()
        linkedin_layout.addRow("Link:", self.link_input)
        self.job_description_input = QPlainTextEdit()
        linkedin_layout.addRow("Job Description:", self.job_description_input)
        self.job_requirements_need_input = QPlainTextEdit()
        linkedin_layout.addRow("Job Requirements - Need:", self.job_requirements_need_input)
        self.job_requirements_nice_input = QPlainTextEdit()
        linkedin_layout.addRow(
            "Job Requirements - Nice to Have:", self.job_requirements_nice_input
        )
        self.enter_data_btn = QPushButton("Enter Data into Google Sheets")
        linkedin_layout.addRow(self.enter_data_btn)

        # Set the content widget as the scroll area's widget
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def _create_connections(self) -> None:
        """
        Connect signals (events) to methods.
        """
        self.enter_data_btn.clicked.connect(lambda: self._send_data_to_google_sheets())

    def _send_data_to_google_sheets(self) -> None:
        """
        Send the gathered data to Google Sheets
        """
        google_sheet_url = self.google_url_line_edit.strip()
        if not google_sheet_url:
            QMessageBox.warning(
                self,
                "Missing URL",
                "Hey you did not set the URL field yet you need to do this!",
            )
            return

        if not self.creds_path or not self.scopes:
            QMessageBox.warning(
                self,
                "Missing Credentials",
                "Google Sheets credentials path or scopes are not set!",
            )
            return

        url = self.link_input.text().strip()
        if url == "":
            url = f"http://example.com/no-link-provided-{random_alphanumeric(12)}"
        job_id = job_id_from_url(url)
        print(f"Generated Job ID: {job_id}")

        google_client = authenticate_google_sheets(self.creds_path, self.scopes)


        field_data = [
            [
                job_id,
                self.job_title_input.text(),
                self.company_input.text(),
                self.location_input.text(),
                self.link_input.text(),
                self.job_description_input.toPlainText().strip().lower(),
                self.job_requirements_need_input.toPlainText().strip().lower(),
                self.job_requirements_nice_input.toPlainText().strip().lower(),
                datetime.datetime.now().strftime("%m/%d/%Y"),
                "No",
            ]
        ]
        pprint(field_data)
        update_google_sheet(
            google_client = google_client,
            google_sheet_url = google_sheet_url,
            data = field_data,
            tab_name = 'manually_entered_data',
        )