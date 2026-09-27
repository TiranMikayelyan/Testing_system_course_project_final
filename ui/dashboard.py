"""Dashboard screen."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import APP_NAME
from ui.widgets import Card, StatCard


class DashboardScreen(QWidget):
    start_test = Signal()
    view_history = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        header = QLabel(f"{APP_NAME}")
        header.setObjectName("appTitle")
        welcome = QLabel("Welcome!")
        welcome.setObjectName("sectionTitle")
        layout.addWidget(header)
        layout.addWidget(welcome)

        stats_row = QHBoxLayout()
        self.stat_completed = StatCard("Tests Completed", "0")
        self.stat_average = StatCard("Average Score", "0%")
        self.stat_best = StatCard("Best Score", "0%")
        stats_row.addWidget(self.stat_completed)
        stats_row.addWidget(self.stat_average)
        stats_row.addWidget(self.stat_best)
        layout.addLayout(stats_row)

        start_btn = QPushButton("START NEW TEST")
        start_btn.setObjectName("primaryBtn")
        start_btn.setMinimumHeight(56)
        start_btn.clicked.connect(self.start_test.emit)
        layout.addWidget(start_btn)

        recent_card = Card()
        recent_title = QLabel("Recent Tests")
        recent_title.setObjectName("sectionTitle")
        self.recent_list = QVBoxLayout()
        self.recent_placeholder = QLabel("No tests completed yet.")
        self.recent_placeholder.setObjectName("subtitle")
        self.recent_list.addWidget(self.recent_placeholder)

        recent_card.add_widget(recent_title)
        recent_card.add_layout(self.recent_list)
        layout.addWidget(recent_card)
        layout.addStretch()

    def update_stats(self, stats: dict) -> None:
        self.stat_completed.set_value(str(stats.get("tests_completed", 0)))
        self.stat_average.set_value(f"{stats.get('average_score', 0)}%")
        self.stat_best.set_value(f"{stats.get('best_score', 0)}%")

        while self.recent_list.count():
            item = self.recent_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        recent = stats.get("recent", [])
        if not recent:
            placeholder = QLabel("No tests completed yet.")
            placeholder.setObjectName("subtitle")
            self.recent_list.addWidget(placeholder)
            return

        for entry in recent:
            row = QHBoxLayout()
            topic = QLabel(entry["topic"])
            topic.setStyleSheet("font-weight: 600;")
            score = QLabel(f"{entry['percentage']:.0f}%")
            score.setStyleSheet("color: #38bdf8; font-weight: 700;")
            row.addWidget(topic)
            row.addStretch()
            row.addWidget(score)
            container = QWidget()
            container.setLayout(row)
            self.recent_list.addWidget(container)
