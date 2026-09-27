"""Quiz screen with timer and question navigation."""

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from config import APP_NAME
from models.test_session import TestSession, TestSessionStatus
from ui.widgets import Card


class QuizScreen(QWidget):
    test_finished = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.session: TestSession | None = None
        self.current_index = 0
        self.remaining_seconds = 0
        self._time_expired = False

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick)

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        top = QHBoxLayout()
        title = QLabel(APP_NAME)
        title.setObjectName("appTitle")
        self.timer_label = QLabel("00:00")
        self.timer_label.setObjectName("timerLabel")
        top.addWidget(title)
        top.addStretch()
        top.addWidget(QLabel("⏱"))
        top.addWidget(self.timer_label)
        layout.addLayout(top)

        self.progress_label = QLabel("Question 1 / 1")
        self.progress_label.setObjectName("sectionTitle")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        layout.addWidget(self.progress_bar)

        self.nav_frame = QFrame()
        self.nav_layout = QHBoxLayout(self.nav_frame)
        self.nav_layout.setSpacing(6)
        layout.addWidget(self.nav_frame)

        self.question_card = Card()
        self.question_text = QLabel("")
        self.question_text.setWordWrap(True)
        self.question_text.setStyleSheet("font-size: 16px; font-weight: 600;")
        self.options_group = QButtonGroup(self)
        self.options_layout = QVBoxLayout()
        self.question_card.add_widget(self.question_text)
        self.question_card.add_layout(self.options_layout)
        layout.addWidget(self.question_card, stretch=1)

        nav_btns = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self._prev_question)
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self._next_question)
        nav_btns.addWidget(self.prev_btn)
        nav_btns.addStretch()
        nav_btns.addWidget(self.next_btn)
        layout.addLayout(nav_btns)

        finish_btn = QPushButton("Finish Test")
        finish_btn.setObjectName("primaryBtn")
        finish_btn.clicked.connect(self._confirm_finish)
        layout.addWidget(finish_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def start_quiz(self, session: TestSession) -> None:
        self.session = session
        self.current_index = 0
        self._time_expired = False
        self.remaining_seconds = session.duration_seconds
        session.start()
        self._update_timer_display()
        self._build_nav_buttons()
        self._show_question(0)
        self.timer.start()

    def _tick(self) -> None:
        if self._time_expired or not self.session:
            return
        self.remaining_seconds -= 1
        self._update_timer_display()
        if self.remaining_seconds <= 0:
            self._time_expired = True
            self.timer.stop()
            self.session.status = TestSessionStatus.EXPIRED
            QMessageBox.information(
                self, "Time's Up", "Time has expired. Your test will be submitted."
            )
            self.test_finished.emit(self.session)

    def _update_timer_display(self) -> None:
        mins, secs = divmod(max(0, self.remaining_seconds), 60)
        self.timer_label.setText(f"{mins:02d}:{secs:02d}")
        if self.remaining_seconds <= 60:
            self.timer_label.setObjectName("timerWarning")
            self.timer_label.style().unpolish(self.timer_label)
            self.timer_label.style().polish(self.timer_label)

    def _build_nav_buttons(self) -> None:
        while self.nav_layout.count():
            item = self.nav_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.session:
            return

        for i in range(self.session.total_questions):
            btn = QPushButton(str(i + 1))
            btn.setFixedSize(36, 36)
            btn.clicked.connect(lambda checked=False, idx=i: self._show_question(idx))
            btn.setProperty("q_index", i)
            self.nav_layout.addWidget(btn)
        self.nav_layout.addStretch()
        self._refresh_nav_states()

    def _refresh_nav_states(self) -> None:
        if not self.session:
            return
        for i in range(self.nav_layout.count()):
            item = self.nav_layout.itemAt(i)
            if not item or not item.widget():
                continue
            btn = item.widget()
            if not isinstance(btn, QPushButton):
                continue
            q = self.session.questions[i]
            answered = self.session.get_answer(q.id) is not None
            if i == self.current_index:
                btn.setStyleSheet(
                    "background-color: #2563eb; color: white; border-radius: 18px;"
                )
            elif answered:
                btn.setStyleSheet(
                    "background-color: #059669; color: white; border-radius: 18px;"
                )
            else:
                btn.setStyleSheet(
                    "background-color: #475569; color: white; border-radius: 18px;"
                )

    def _show_question(self, index: int) -> None:
        if not self.session or self._time_expired:
            return
        self.current_index = index
        question = self.session.questions[index]

        self.progress_label.setText(
            f"Question {index + 1} / {self.session.total_questions}"
        )
        self.progress_bar.setMaximum(self.session.total_questions)
        self.progress_bar.setValue(index + 1)
        self.question_text.setText(question.question)

        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.options_group = QButtonGroup(self)

        current_answer = self.session.get_answer(question.id)
        for option in question.options:
            radio = QRadioButton(option)
            if current_answer == option:
                radio.setChecked(True)
            radio.toggled.connect(
                lambda checked, opt=option: self._select_answer(opt) if checked else None
            )
            self.options_group.addButton(radio)
            self.options_layout.addWidget(radio)

        self.prev_btn.setEnabled(index > 0)
        self.next_btn.setEnabled(index < self.session.total_questions - 1)
        self._refresh_nav_states()

    def _select_answer(self, option: str) -> None:
        if not self.session or self._time_expired:
            return
        q = self.session.questions[self.current_index]
        self.session.set_answer(q.id, option)
        self._refresh_nav_states()

    def _prev_question(self) -> None:
        if self.current_index > 0:
            self._show_question(self.current_index - 1)

    def _next_question(self) -> None:
        if self.session and self.current_index < self.session.total_questions - 1:
            self._show_question(self.current_index + 1)

    def _confirm_finish(self) -> None:
        if not self.session or self._time_expired:
            return
        unanswered = self.session.total_questions - self.session.answered_count()
        msg = "Submit your test?"
        if unanswered:
            msg += f"\n\nYou have {unanswered} unanswered question(s)."
        reply = QMessageBox.question(self, "Finish Test", msg)
        if reply == QMessageBox.StandardButton.Yes:
            self.timer.stop()
            self.test_finished.emit(self.session)

    def reset(self) -> None:
        self.timer.stop()
        self.session = None
        self._time_expired = False
