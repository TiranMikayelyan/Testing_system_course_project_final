"""Answer review screen."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from models.test_result import TestResultData
from ui.widgets import Card


class ReviewScreen(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        title = QLabel("Answer Review")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.review_container = QWidget()
        self.review_layout = QVBoxLayout(self.review_container)
        self.review_layout.setSpacing(12)
        scroll.setWidget(self.review_container)
        layout.addWidget(scroll)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.back_requested.emit)
        layout.addWidget(back_btn)

    def show_review(self, result: TestResultData) -> None:
        while self.review_layout.count():
            item = self.review_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, item in enumerate(result.review_items, start=1):
            card = Card()
            q_label = QLabel(f"Question {i}")
            q_label.setStyleSheet("font-weight: 700;")
            text = QLabel(item.question_text)
            text.setWordWrap(True)

            your = QLabel(
                f"Your answer:\n{item.user_answer or '—'}"
            )
            correct = QLabel(f"Correct answer:\n{item.correct_answer}")

            if item.is_unanswered:
                status = QLabel("○ Unanswered")
                status.setStyleSheet("color: #94a3b8; font-weight: 700;")
            elif item.is_correct:
                status = QLabel("✓ Correct")
                status.setStyleSheet("color: #22c55e; font-weight: 700;")
            else:
                status = QLabel("✗ Incorrect")
                status.setStyleSheet("color: #ef4444; font-weight: 700;")

            card.add_widget(q_label)
            card.add_widget(text)
            card.add_widget(your)
            card.add_widget(correct)
            card.add_widget(status)
            self.review_layout.addWidget(card)

        self.review_layout.addStretch()
