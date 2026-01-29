import sys
import json
import webbrowser
from pathlib import Path
from job_scanner.utils.logger_setup import start_logger

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QComboBox,
    QMessageBox,
    QDialog,
    QPlainTextEdit
)


LOG = start_logger()

_app = None
_window = None

class AboutDialog(QDialog):
    def __init__(self, version: str, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About Job Scanner")
        self.setFixedSize(420, 300)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("<b>Job Scanner</b>")
        version = QLabel(f"Version {version}")

        description = QLabel(
            "I got so tiered of looking for new jobs so I built a tool to speed"
            "up the process of doing this. This tool will scrape from websites and"
            "put that data into a google sheet and from there rate and categorize"
            "the jobs you find."
        )
        description.setWordWrap(True)

        links = QLabel(
            """
            <a href="https://github.com/markC85">GitHub</a><br>
            <a href="https://mark_conrad.artstation.com">Animation Portfolio</a>
            <a href="http://www.linkedin.com/in/markaconrad">Linkedin Profile</a>
            """
        )
        links.setOpenExternalLinks(True)
        links.setTextInteractionFlags(Qt.TextBrowserInteraction)
        links.setCursor(Qt.PointingHandCursor)

        email = QLabel("Email: markconrad.animator@gmail.com")
        email.setTextInteractionFlags(Qt.TextBrowserInteraction)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(version)
        layout.addWidget(description)
        layout.addSpacing(10)
        layout.addWidget(links)
        layout.addWidget(email)
        layout.addStretch()
        layout.addWidget(close_btn)

class MainWindow(QMainWindow):
    """
    Main application window
    """
    def __init__(self):
        super().__init__()

        self.version = "1.0.0"
        self.setWindowTitle(f"Job Scanner {self.version}")
        self.resize(500, 800)

        self._ui_widgets()
        self._create_menu()
        self._create_connections()

    def _save_field_presets(self) -> None:
        """
        Save the current field presets to a file
        """
        field_data = self._gather_field_information()
        field_data["google_sheet_scope"] = self.google_sheet_scope.toPlainText()
        field_data["linkedin_search_pair"] = self.linkedin_search_pair.toPlainText()

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Preset", "", "JSON Files (*.json)"
        )

        if not file_path:
            return

        with Path(file_path).open("w", encoding="utf-8") as f:
            json.dump(field_data, f, ensure_ascii=False, indent=4)

    def _load_field_presets(self) -> None:
        """
        This will load fields presets from a JSON file
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Preset", "", "JSON Files (*.json)"
        )

        if not file_path:
            return

        json_path = Path(file_path)

        try:
            with json_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Failed",
                f"Could not read preset file:\n{e}\nJSON File: {json_path}",
            )
            return

        field_data = {}
        for widget in self.centralWidget().findChildren(QLineEdit):
            label = widget.previousInFocusChain()
            if isinstance(label, QLabel):
                field_data[label.text().strip(":")] = widget

        # Populate fields safely
        for key, widget in field_data.items():
            value = data.get(key, "")
            widget.setText(value)

        self.google_sheet_scope.setPlainText(data.get("google_sheet_scope", ""))
        self.linkedin_search_pair.setPlainText(data.get("linkedin_search_pair", ""))

    def _ui_widgets(self) -> None:
        """
        UI fields and layout
        """
        # button style sheets
        button_style = """
            QPushButton {
                background-color: #f39c12;   /* orange */
                color: black;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;   /* darker orange */
            }
            QPushButton:pressed {
                background-color: #d35400;   /* even darker */
            }
        """

        # Scroll area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scrape_websites_btn = QPushButton("Scrape Websites")
        self.scrape_websites_btn.setStyleSheet(button_style)

        self.rate_jobs_btn = QPushButton("Rate Jobs with LLM and Data Points")
        self.rate_jobs_btn.setStyleSheet(button_style)

        tool_description = (
            "This tool will help you scrape job postings from various websites and rate them \n"
            "based on your resume using a Large Language Model (LLM). You can start by scraping \n"
            "job postings, and then proceed to rate them to see how well they match your resume."
        )

        tool_description_label = QLabel(tool_description)

        labels_fields = [
            "PDF File to Compare Path:",
            "AI API Key Path:",
            "Google Sheet Credentials JSON Path:",
            "Google Sheet URL:",
        ]

        self.google_sheet_scope = QPlainTextEdit()
        self.google_sheet_scope.setPlaceholderText(
            "Add URL for Google Sheet and scopes, one per line.\n"
            "Example:\n"
            "https://www.googleapis.com/auth/spreadsheets\n"
            "https://www.googleapis.com/auth/drive"
        )
        scope_label = QLabel("Google Sheet Scopes:")

        self.linkedin_search_pair = QPlainTextEdit()
        self.linkedin_search_pair.setPlaceholderText(
            "Add your search pairs for linkedin scrape job.\n"
            "Example:\n"
            "[Job Title],[Location]\n"
            "Software Engineer,New York, NY\n"
            "Data Scientist,San Francisco, CA"
        )
        linkedin_search_pair_label = QLabel("Google Sheet Scopes:")

        main_layout.addWidget(tool_description_label)
        main_layout.addWidget(scope_label)
        main_layout.addWidget(self.google_sheet_scope)
        main_layout.addWidget(linkedin_search_pair_label)
        main_layout.addWidget(self.linkedin_search_pair)

        for label_text in labels_fields:
            label = QLabel(label_text)
            main_layout.addWidget(label)

            if label_text == "PDF File to Compare Path:":
                self.set_pdf_file_path_line_edit = QLineEdit()
                self.set_pdf_file_path_line_edit.setPlaceholderText(f"Enter {label_text.lower()[:-1]}")
                main_layout.addWidget(self.set_pdf_file_path_line_edit)
                self.set_pdf_file_path_btn = QPushButton(f"Set {label_text.lower()[:-1]}")
                main_layout.addWidget(self.set_pdf_file_path_btn)
            elif label_text == "AI API Key Path:":
                self.set_api_key_path_line_edit = QLineEdit()
                self.set_api_key_path_line_edit.setPlaceholderText(f"Enter {label_text.lower()[:-1]}")
                main_layout.addWidget(self.set_api_key_path_line_edit)
                self.set_api_key_path_btn = QPushButton(f"Set {label_text.lower()[:-1]}")
                main_layout.addWidget(self.set_api_key_path_btn)
            elif label_text == "Google Sheet Credentials JSON Path:":
                self.set_google_sheet_path_line_edit = QLineEdit()
                self.set_google_sheet_path_line_edit.setPlaceholderText(f"Enter {label_text.lower()[:-1]}")
                main_layout.addWidget(self.set_google_sheet_path_line_edit)
                self.set_google_sheet_path_btn = QPushButton(f"Set {label_text.lower()[:-1]}")
                main_layout.addWidget(self.set_google_sheet_path_btn)
            else:
                line_edit = QLineEdit()
                line_edit.setPlaceholderText(f"Enter {label_text.lower()[:-1]}")
                main_layout.addWidget(line_edit)

        main_layout.addWidget(self.scrape_websites_btn)
        main_layout.addWidget(self.rate_jobs_btn)

        # Set the content widget as the scroll area's widget
        scroll_area.setWidget(content_widget)
        self.setCentralWidget(scroll_area)

    def _create_menu(self) -> None:
        """
        Create the menu bar with File -> Exit
        """

        # Create the menu bar
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        help_menu = menu_bar.addMenu("Help")

        # about menu options
        self.about_project = QAction("About", self)
        self.about_project.setStatusTip("About this project")

        # exit action
        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.setStatusTip("Exit the application")

        # save fields presets
        self.save_preset = QAction("Save Preset", self)
        self.save_preset.setShortcut("Ctrl+S")
        self.save_preset.setStatusTip("Save fields preset")

        # load fields presets
        self.load_preset = QAction("Load Preset", self)
        self.load_preset.setShortcut("Ctrl+O")
        self.load_preset.setStatusTip("Load fields preset")

        # load webpage for scrapper
        self.google_sheet = QAction("Open Google Sheets", self)
        self.google_sheet.setShortcut("Ctrl+G")
        self.google_sheet.setStatusTip("Open Google Sheets in your browser")

        # Add the action to the File menu
        file_menu.addAction(self.save_preset)
        file_menu.addAction(self.load_preset)
        file_menu.addAction(self.google_sheet)
        file_menu.addAction(self.exit_action)

        # Add the action to the About menu
        help_menu.addAction(self.about_project)

    def _gather_field_information(self) -> dict:
        """
        Gather all the information from the UI fields

        Returns:
            field_data (dict): A dictionary with all the field names and their values
        """
        field_data = {}
        for widget in self.centralWidget().findChildren(QLineEdit):
            label = widget.previousInFocusChain()
            if isinstance(label, QLabel):
                field_data[label.text().strip(":")] = widget.text()

        return field_data

    def _create_connections(self) -> None:
        """
        Connect signals (events) to methods.
        """
        self.set_pdf_file_path_btn.clicked.connect(
            lambda: self._set_file_path(
                "Select the PDF Resume you want to use",
                "PDF File to Compare Path",
                "*.pdf",
            )
        )
        self.set_api_key_path_btn.clicked.connect(
            lambda: self._set_file_path(
                "Select the AI API Key file",
                "AI API Key Path",
                "*.json"
            )
        )
        self.set_google_sheet_path_btn.clicked.connect(
            lambda: self._set_file_path(
                "Select the Google Sheet Credentials JSON file",
                "Google Sheet Credentials JSON Path",
                "*.json",
            )
        )

        self.save_preset.triggered.connect(self._save_field_presets)
        self.load_preset.triggered.connect(self._load_field_presets)
        self.exit_action.triggered.connect(self.close)

        link = "https://docs.google.com/spreadsheets/d/1D992PCSaAX-L648D26jMa4fSVtMaOIp5Y34TpYY4ajM/edit?gid=0#gid=0"
        self.google_sheet.triggered.connect(lambda: webbrowser.open(link))

        self.about_project.triggered.connect(self._show_about_dialog)

        self.scrape_websites_btn.clicked.connect(self._run_scrape_websites)
        self.rate_jobs_btn.clicked.connect(self._run_rate_jobs)

    def _run_scrape_websites(self) -> None:
        """
        This will run the scrape websites function
        """
        from job_scanner.main import job_scanner
        field_data = self._gather_field_information()
        queries = []
        for line in self.linkedin_search_pair.toPlainText().splitlines():
            if "," in line:
                job_title, location = line.split(",", 1)
                queries.append((job_title.strip(), location.strip()))
        scopes = self.google_sheet_scope.toPlainText().splitlines()

        job_scanner(
            queries=queries,
            service_account_file=field_data["Google Sheet Credentials JSON Path"],
            scopes=scopes,
            google_sheet_url=field_data["Google Sheet URL"],
        )

    def _run_rate_jobs(self) -> None:
        """
        This will run the rate jobs function
        """
        from job_scanner.main import job_ratter
        field_data = self._gather_field_information()
        scopes = self.google_sheet_scope.toPlainText().splitlines()

        job_ratter(
            pdf_file_path=field_data["PDF File to Compare Path"],
            json_token_path=field_data["AI API Key Path"],
            service_account_file=field_data["Google Sheet Credentials JSON Path"],
            scopes=scopes,
            google_sheet_url=field_data["Google Sheet URL"],
        )

    def _show_about_dialog(self) -> None:
        dlg = AboutDialog(self.version, self)
        dlg.exec()

    def _set_file_path(self,description: str, filed_to_fill_out: str, file_filter: str) -> None:
        """
        This will set the resume path field
        description (str): Description for the file dialog
        filed_to_fill_out (str): The field to fill out with the selected file path
        file_filter (str): The file filter for the dialog
        """
        file_path, _ = QFileDialog.getOpenFileName(self, description, "", file_filter)

        if not file_path:
            return

        file_path = file_path.replace("/", "\\")
        if filed_to_fill_out == "PDF File to Compare Path":
            self.set_pdf_file_path_line_edit.setText(file_path)
        elif filed_to_fill_out == "AI API Key Path":
            self.set_api_key_path_line_edit.setText(file_path)
        elif filed_to_fill_out == "Google Sheet Credentials JSON Path":
            self.set_google_sheet_path_line_edit.setText(file_path)

def show_ui() -> MainWindow:
    """
    This will show the main UI window for the application

    Returns:
        MainWindow: The main window instance
    """
    global _app, _window

    _app = QApplication.instance() or QApplication(sys.argv)

    if _window:
        LOG.debug("Main window already exists, closing the existing one.")
        _window.close()
        _window.deleteLater()

    _window = MainWindow()
    _window.show()

    return _window

# start the UI
show_ui()
sys.exit(_app.exec())