"""Settings screen."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import QUESTION_COUNTS, TIME_LIMITS
from ui.widgets import Card


class SettingsScreen(QWidget):
    settings_saved = Signal(dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        title = QLabel("Settings")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        card = Card()
        form = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])

        self.sound_check = QCheckBox("Enable sound effects")

        self.language_combo = QComboBox()
        self.language_combo.addItems(["en", "ru"])

        self.default_questions = QComboBox()
        for c in QUESTION_COUNTS:
            self.default_questions.addItem(str(c), c)

        self.default_duration = QComboBox()
        for label, minutes in TIME_LIMITS.items():
            self.default_duration.addItem(label, minutes)

        form.addRow("Theme", self.theme_combo)
        form.addRow("Sound", self.sound_check)
        form.addRow("Language", self.language_combo)
        form.addRow("Default Questions", self.default_questions)
        form.addRow("Default Duration", self.default_duration)
        card.add_layout(form)
        layout.addWidget(card)

        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)
        layout.addStretch()

    def load_settings(self, settings: dict) -> None:
        idx = self.theme_combo.findText(settings.get("theme", "dark"))
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        self.sound_check.setChecked(settings.get("sound_enabled", True))
        lang_idx = self.language_combo.findText(settings.get("language", "en"))
        if lang_idx >= 0:
            self.language_combo.setCurrentIndex(lang_idx)
        q_idx = self.default_questions.findData(settings.get("default_questions", 10))
        if q_idx >= 0:
            self.default_questions.setCurrentIndex(q_idx)
        d_idx = self.default_duration.findData(settings.get("default_duration", 15))
        if d_idx >= 0:
            self.default_duration.setCurrentIndex(d_idx)

    def _save(self) -> None:
        self.settings_saved.emit(
            {
                "theme": self.theme_combo.currentText(),
                "sound_enabled": self.sound_check.isChecked(),
                "language": self.language_combo.currentText(),
                "default_questions": self.default_questions.currentData(),
                "default_duration": self.default_duration.currentData(),
            }
        )
