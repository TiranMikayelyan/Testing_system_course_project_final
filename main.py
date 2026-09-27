"""Online Testing System — entry point."""

import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from database.database import init_db
from ui.main_window import MainWindow


def _log_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "testing_system.log"
    return Path(__file__).resolve().parent / "testing_system.log"


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(_log_path(), encoding="utf-8"),
        ],
    )


def main() -> int:
    setup_logging()
    init_db()

    app = QApplication(sys.argv)
    app.setApplicationName("Online Testing System")
    app.setOrganizationName("TestingSystem")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
