"""Main application window with sidebar navigation."""

import logging

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config import APP_NAME
from database.database import get_session
from models.user import User
from services.question_service import QuestionServiceError
from services.test_service import TestService
from services.user_service import UserService
from ui.about import AboutScreen
from ui.dashboard import DashboardScreen
from ui.history import HistoryScreen
from ui.login import LoginScreen
from ui.quiz_window import QuizScreen
from ui.results import ResultsScreen
from ui.review import ReviewScreen
from ui.settings import SettingsScreen
from ui.styles import get_theme_stylesheet
from ui.test_setup import TestSetupScreen
from ui.widgets import LoadingOverlay

logger = logging.getLogger(__name__)

# Screen indices
LOGIN = 0
DASHBOARD = 1
TEST_SETUP = 2
QUIZ = 3
RESULTS = 4
REVIEW = 5
HISTORY = 6
SETTINGS = 7
ABOUT = 8


class QuestionLoaderThread(QThread):
    finished_ok = Signal(object)
    failed = Signal(str)

    def __init__(self, test_service: TestService, config: dict, user_id: int):
        super().__init__()
        self.test_service = test_service
        self.config = config
        self.user_id = user_id

    def run(self) -> None:
        try:
            session = self.test_service.create_session(
                user_id=self.user_id,
                topic=self.config["topic"],
                question_count=self.config["question_count"],
                duration_minutes=self.config["duration_minutes"],
                points_per_question=self.config.get("points_per_question", 1),
            )
            self.finished_ok.emit(session)
        except QuestionServiceError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:
            logger.exception("Unexpected error loading questions")
            self.failed.emit(f"An unexpected error occurred: {exc}")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)

        self.db = get_session()
        self.user_service = UserService(self.db)
        self.test_service = TestService(self.db)
        self.current_user: User | None = None
        self.current_result = None
        self._loader_thread: QuestionLoaderThread | None = None
        self._settings = {}

        self._build_ui()
        self._connect_signals()
        self.show_login()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(12, 20, 12, 20)
        sidebar_layout.setSpacing(6)

        brand = QLabel(APP_NAME)
        brand.setObjectName("appTitle")
        brand.setWordWrap(True)
        sidebar_layout.addWidget(brand)

        self.user_label = QLabel("")
        self.user_label.setObjectName("subtitle")
        sidebar_layout.addWidget(self.user_label)
        sidebar_layout.addSpacing(16)

        self.nav_buttons: dict[str, QPushButton] = {}
        nav_items = [
            ("dashboard", "Dashboard", DASHBOARD),
            ("setup", "Test Setup", TEST_SETUP),
            ("history", "History", HISTORY),
            ("settings", "Settings", SETTINGS),
            ("about", "About", ABOUT),
        ]
        for key, label, index in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("navBtn")
            btn.setProperty("active", False)
            btn.clicked.connect(lambda checked=False, i=index, k=key: self._navigate(i, k))
            self.nav_buttons[key] = btn
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self._logout)
        sidebar_layout.addWidget(self.logout_btn)

        self.stack = QStackedWidget()
        self.login_screen = LoginScreen(self.user_service)
        self.dashboard_screen = DashboardScreen()
        self.test_setup_screen = TestSetupScreen()
        self.quiz_screen = QuizScreen()
        self.results_screen = ResultsScreen()
        self.review_screen = ReviewScreen()
        self.history_screen = HistoryScreen()
        self.settings_screen = SettingsScreen()
        self.about_screen = AboutScreen()

        for screen in [
            self.login_screen,
            self.dashboard_screen,
            self.test_setup_screen,
            self.quiz_screen,
            self.results_screen,
            self.review_screen,
            self.history_screen,
            self.settings_screen,
            self.about_screen,
        ]:
            self.stack.addWidget(screen)

        root.addWidget(self.sidebar)
        root.addWidget(self.stack, stretch=1)

        self.loading_overlay = LoadingOverlay("Loading questions...", self.stack)
        self.loading_overlay.hide()
        self.sidebar.hide()

    def _connect_signals(self) -> None:
        self.login_screen.login_success.connect(self._on_auth)
        self.login_screen.register_success.connect(self._on_auth)

        self.dashboard_screen.start_test.connect(lambda: self._navigate(TEST_SETUP, "setup"))
        self.test_setup_screen.start_test.connect(self._start_test_loading)
        self.quiz_screen.test_finished.connect(self._finish_test)
        self.results_screen.review_requested.connect(self._show_review)
        self.results_screen.new_test.connect(lambda: self._navigate(TEST_SETUP, "setup"))
        self.results_screen.dashboard.connect(lambda: self._navigate(DASHBOARD, "dashboard"))
        self.review_screen.back_requested.connect(self._review_back)
        self.history_screen.result_selected.connect(self._load_history_result)
        self.settings_screen.settings_saved.connect(self._save_settings)

    def show_login(self) -> None:
        self.current_user = None
        self.sidebar.hide()
        self.stack.setCurrentIndex(LOGIN)

    def _on_auth(self, user: User) -> None:
        self.current_user = user
        self.user_label.setText(user.display_name)
        self._settings = self.user_service.get_settings(user.id)
        self._apply_theme(self._settings.get("theme", "dark"))
        self.settings_screen.load_settings(self._settings)
        self.test_setup_screen.apply_defaults(self._settings)
        self.sidebar.show()
        self._refresh_dashboard()
        self._navigate(DASHBOARD, "dashboard")

    def _logout(self) -> None:
        reply = QMessageBox.question(self, "Logout", "Sign out of your account?")
        if reply == QMessageBox.StandardButton.Yes:
            self.quiz_screen.reset()
            self.show_login()

    def _navigate(self, index: int, nav_key: str | None = None) -> None:
        if index != LOGIN and not self.current_user:
            return
        if index == HISTORY:
            self._refresh_history()
        if index == DASHBOARD:
            self._refresh_dashboard()
        if index == SETTINGS and self.current_user:
            self.settings_screen.load_settings(
                self.user_service.get_settings(self.current_user.id)
            )

        self.stack.setCurrentIndex(index)
        for key, btn in self.nav_buttons.items():
            btn.setProperty("active", key == nav_key)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _refresh_dashboard(self) -> None:
        if not self.current_user:
            return
        stats = self.user_service.get_statistics(self.current_user.id)
        self.dashboard_screen.update_stats(stats)

    def _refresh_history(self) -> None:
        if not self.current_user:
            return
        history = self.test_service.get_history(self.current_user.id)
        self.history_screen.load_history(history)

    def _start_test_loading(self, config: dict) -> None:
        if not self.current_user:
            return
        self.loading_overlay.setGeometry(self.stack.rect())
        self.loading_overlay.show()
        self.loading_overlay.raise_()

        self._loader_thread = QuestionLoaderThread(
            self.test_service, config, self.current_user.id
        )
        self._loader_thread.finished_ok.connect(self._on_questions_loaded)
        self._loader_thread.failed.connect(self._on_questions_failed)
        self._loader_thread.start()

    def _on_questions_loaded(self, session) -> None:
        self.loading_overlay.hide()
        self.quiz_screen.start_quiz(session)
        self.stack.setCurrentIndex(QUIZ)

    def _on_questions_failed(self, message: str) -> None:
        self.loading_overlay.hide()
        QMessageBox.critical(
            self,
            "Unable to Load Questions",
            f"{message}\n\nPlease check your Internet connection and try again.",
        )

    def _finish_test(self, session) -> None:
        expired = session.status.value == "expired"
        result = self.test_service.submit_session(session, expired=expired)
        self.current_result = result
        self.results_screen.show_result(result)
        self.quiz_screen.reset()
        self._refresh_dashboard()
        self.stack.setCurrentIndex(RESULTS)

    def _show_review(self, result) -> None:
        self.current_result = result
        self.review_screen.show_review(result)
        self.stack.setCurrentIndex(REVIEW)

    def _review_back(self) -> None:
        if self.current_result:
            self.stack.setCurrentIndex(RESULTS)
        else:
            self._navigate(HISTORY, "history")

    def _load_history_result(self, result_id: int) -> None:
        if not self.current_user:
            return
        result = self.test_service.load_result(result_id, self.current_user.id)
        if result:
            self.current_result = result
            self.review_screen.show_review(result)
            self.stack.setCurrentIndex(REVIEW)
        else:
            QMessageBox.warning(self, "Error", "Could not load test result.")

    def _save_settings(self, settings: dict) -> None:
        if not self.current_user:
            return
        self.user_service.save_settings(self.current_user.id, settings)
        self._settings = settings
        self._apply_theme(settings.get("theme", "dark"))
        self.test_setup_screen.apply_defaults(settings)
        QMessageBox.information(self, "Settings", "Settings saved successfully.")

    def _apply_theme(self, theme: str) -> None:
        self.setStyleSheet(get_theme_stylesheet(theme))

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, "loading_overlay"):
            self.loading_overlay.setGeometry(self.stack.rect())

    def closeEvent(self, event) -> None:
        self.db.close()
        super().closeEvent(event)
