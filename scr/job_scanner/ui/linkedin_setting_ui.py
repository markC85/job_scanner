from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QDialog,
    QFormLayout,
    QComboBox
)


class LinkedinSettings(QDialog):
    def __init__(self, version: str, parent=None):
        super().__init__(parent)

        self._ui_widgets(version)
        self._create_connections()

    def _ui_widgets(self,version):
        """
        UI fields and layout
        """
        self.setWindowTitle(f"LinkedIn Scanner Options v.{version}")
        self.resize(420, 300)

        main_layout = QVBoxLayout(self)

        # Scroll area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        linkedin_layout = QFormLayout(content_widget)
        linkedin_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.rate_jobs_btn = QPushButton("Set Linkedin Scanner Options")

        self.date_range_combo = QComboBox()
        self.date_range_combo.addItems(
            [
                "24 hours",
                "7 days",
                "30 days",
            ]
        )

        self.work_type = QComboBox()
        self.work_type.addItems(
            [
                "On-Site",
                "Remote",
                "Hybrid",
            ]
        )

        self.pages_to_scrape = QLineEdit()
        self.pages_to_scrape.setValidator(QIntValidator(1, 100))

        linkedin_layout.addRow("Work Type:", self.work_type)
        linkedin_layout.addRow("Job Type:", QLineEdit())
        linkedin_layout.addRow("Post Date:", self.date_range_combo)
        linkedin_layout.addRow("Pages to Scrape:", self.pages_to_scrape)

        # Set the content widget as the scroll area's widget
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def _create_connections(self) -> None:
        """
        Connect signals (events) to methods.
        """
        pass