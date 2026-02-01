from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QDialog,
)


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