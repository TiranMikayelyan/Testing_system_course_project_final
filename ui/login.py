"""Login and registration screen."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config import APP_NAME
from ui.widgets import Card


class LoginScreen(QWidget):
    login_success = Signal(object)
    register_success = Signal(object)

    def __init__(self, user_service, parent=None) -> None:
        super().__init__(parent)
        self.user_service = user_service
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = Card()
        card.setFixedWidth(420)
        self.stack = QStackedWidget()

        self.stack.addWidget(self._login_form())
        self.stack.addWidget(self._register_form())
        card.add_widget(self.stack)
        root.addWidget(card)

    def _login_form(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(14)

        title = QLabel(APP_NAME)
        title.setObjectName("appTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel("Sign in to continue")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Username")
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)

        login_btn = QPushButton("Sign In")
        login_btn.setObjectName("primaryBtn")
        login_btn.clicked.connect(self._do_login)

        switch = QPushButton("Create an account")
        switch.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)
        layout.addWidget(self.login_username)
        layout.addWidget(self.login_password)
        layout.addWidget(login_btn)
        layout.addWidget(switch, alignment=Qt.AlignmentFlag.AlignCenter)
        return w

    def _register_form(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        title = QLabel("Create Account")
        title.setObjectName("sectionTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Username")
        self.reg_display = QLineEdit()
        self.reg_display.setPlaceholderText("Display name (optional)")
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Password (min 6 chars)")
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)

        reg_btn = QPushButton("Register")
        reg_btn.setObjectName("primaryBtn")
        reg_btn.clicked.connect(self._do_register)

        back = QPushButton("Back to Sign In")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        layout.addWidget(title)
        layout.addSpacing(8)
        layout.addWidget(self.reg_username)
        layout.addWidget(self.reg_display)
        layout.addWidget(self.reg_password)
        layout.addWidget(reg_btn)
        layout.addWidget(back, alignment=Qt.AlignmentFlag.AlignCenter)
        return w

    def _do_login(self) -> None:
        try:
            user = self.user_service.login(
                self.login_username.text(), self.login_password.text()
            )
            self.login_success.emit(user)
        except Exception as exc:
            QMessageBox.warning(self, "Login Failed", str(exc))

    def _do_register(self) -> None:
        try:
            user = self.user_service.register(
                self.reg_username.text(),
                self.reg_password.text(),
                self.reg_display.text(),
            )
            self.register_success.emit(user)
        except Exception as exc:
            QMessageBox.warning(self, "Registration Failed", str(exc))
