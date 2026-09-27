"""Test setup screen."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import POINTS_PER_QUESTION, QUESTION_COUNTS, TIME_LIMITS, TOPICS
from ui.widgets import Card


class TestSetupScreen(QWidget):
    start_test = Signal(dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._defaults = {"questions": 10, "duration": 15}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        title = QLabel("Test Setup")
        title.setObjectName("sectionTitle")
        subtitle = QLabel("Configure your test before starting")
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = Card()
        form = QFormLayout()
        form.setSpacing(16)

        self.topic_combo = QComboBox()
        self.topic_combo.addItems(TOPICS)

        self.questions_combo = QComboBox()
        for c in QUESTION_COUNTS:
            self.questions_combo.addItem(str(c), c)

        self.time_combo = QComboBox()
        for label, minutes in TIME_LIMITS.items():
            self.time_combo.addItem(label, minutes)

        self.points_label = QLabel(f"{POINTS_PER_QUESTION} point per question")

        form.addRow("Topic", self.topic_combo)
        form.addRow("Number of Questions", self.questions_combo)
        form.addRow("Time Limit", self.time_combo)
        form.addRow("Points", self.points_label)

        card.add_layout(form)
        layout.addWidget(card)

        start_btn = QPushButton("START TEST")
        start_btn.setObjectName("primaryBtn")
        start_btn.setMinimumHeight(48)
        start_btn.clicked.connect(self._emit_start)
        layout.addWidget(start_btn)
        layout.addStretch()

    def apply_defaults(self, settings: dict) -> None:
        self._defaults = settings
        q_idx = self.questions_combo.findData(settings.get("default_questions", 10))
        if q_idx >= 0:
            self.questions_combo.setCurrentIndex(q_idx)
        d_idx = self.time_combo.findData(settings.get("default_duration", 15))
        if d_idx >= 0:
            self.time_combo.setCurrentIndex(d_idx)

    def _emit_start(self) -> None:
        self.start_test.emit(
            {
                "topic": self.topic_combo.currentText(),
                "question_count": self.questions_combo.currentData(),
                "duration_minutes": self.time_combo.currentData(),
                "points_per_question": POINTS_PER_QUESTION,
            }
        )
