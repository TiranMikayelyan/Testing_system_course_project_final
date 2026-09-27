"""About screen."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from config import APP_NAME, APP_VERSION
from ui.widgets import Card


class AboutScreen(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        card = Card()

        title = QLabel(APP_NAME)
        title.setObjectName("appTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        version = QLabel(f"Version {APP_VERSION}")
        version.setObjectName("subtitle")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc = QLabel(
            "A modern desktop testing application built with Python and PySide6.\n\n"
            "Questions are fetched dynamically from Open Trivia DB (opentdb.com).\n\n"
            "Features:\n"
            "• Topic-based multiple choice tests\n"
            "• Countdown timer with auto-submit\n"
            "• Score evaluation and answer review\n"
            "• Local user accounts and test history\n"
            "• SQLite database for results storage"
        )
        desc.setWordWrap(True)
        desc.setObjectName("subtitle")

        card.add_widget(title)
        card.add_widget(version)
        card.add_widget(desc)
        layout.addWidget(card)
        layout.addStretch()
