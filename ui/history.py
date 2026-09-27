"""Test history screen."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class HistoryScreen(QWidget):
    result_selected = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._history: list[dict] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        title = QLabel("Test History")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Date", "Topic", "Score", "Percentage"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        view_btn = QPushButton("Review Selected Result")
        view_btn.setObjectName("primaryBtn")
        view_btn.clicked.connect(self._view_selected)
        layout.addWidget(view_btn)

    def load_history(self, history: list[dict]) -> None:
        self._history = history
        self.table.setRowCount(len(history))
        for row, entry in enumerate(history):
            date_str = entry["date"].strftime("%d/%m/%Y %H:%M")
            self.table.setItem(row, 0, QTableWidgetItem(date_str))
            self.table.setItem(row, 1, QTableWidgetItem(entry["topic"]))
            self.table.setItem(
                row, 2, QTableWidgetItem(f"{entry['score']}/{entry['max_score']}")
            )
            self.table.setItem(
                row, 3, QTableWidgetItem(f"{entry['percentage']:.0f}%")
            )

    def _view_selected(self) -> None:
        row = self.table.currentRow()
        if row >= 0 and row < len(self._history):
            self.result_selected.emit(self._history[row]["id"])
