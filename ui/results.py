"""Test results screen."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from models.test_result import TestResultData
from ui.widgets import Card, StatCard


class ResultsScreen(QWidget):
    review_requested = Signal(object)
    new_test = Signal()
    dashboard = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.result: TestResultData | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)

        title = QLabel("TEST COMPLETED")
        title.setObjectName("sectionTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.percentage_label = QLabel("0%")
        self.percentage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.percentage_label.setStyleSheet("font-size: 48px; font-weight: 800; color: #38bdf8;")
        layout.addWidget(self.percentage_label)

        self.score_label = QLabel("0 / 0")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(self.score_label)

        self.result_bar = QProgressBar()
        self.result_bar.setFixedHeight(14)
        self.result_bar.setTextVisible(True)
        layout.addWidget(self.result_bar)

        stats = QHBoxLayout()
        self.correct_card = StatCard("Correct", "0")
        self.wrong_card = StatCard("Wrong", "0")
        self.unanswered_card = StatCard("Unanswered", "0")
        stats.addWidget(self.correct_card)
        stats.addWidget(self.wrong_card)
        stats.addWidget(self.unanswered_card)
        layout.addLayout(stats)

        btns = QHBoxLayout()
        review_btn = QPushButton("Review Answers")
        review_btn.setObjectName("primaryBtn")
        review_btn.clicked.connect(self._review)
        new_btn = QPushButton("Start New Test")
        new_btn.clicked.connect(self.new_test.emit)
        home_btn = QPushButton("Dashboard")
        home_btn.clicked.connect(self.dashboard.emit)
        btns.addWidget(review_btn)
        btns.addWidget(new_btn)
        btns.addWidget(home_btn)
        layout.addLayout(btns)
        layout.addStretch()

    def show_result(self, result: TestResultData) -> None:
        self.result = result
        self.percentage_label.setText(f"{result.percentage:.0f}%")
        self.score_label.setText(f"{result.score} / {result.max_score}")
        self.result_bar.setMaximum(result.max_score)
        self.result_bar.setValue(result.score)
        self.result_bar.setFormat(f"{result.percentage:.0f}%")
        self.correct_card.set_value(str(result.correct))
        self.wrong_card.set_value(str(result.incorrect))
        self.unanswered_card.set_value(str(result.unanswered))

    def _review(self) -> None:
        if self.result:
            self.review_requested.emit(self.result)
