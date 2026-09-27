"""Application-wide Qt stylesheets."""

DARK_THEME = """
QMainWindow, QWidget {
    background-color: #0f172a;
    color: #e2e8f0;
    font-family: "Segoe UI", sans-serif;
    font-size: 14px;
}
QFrame#sidebar {
    background-color: #1e293b;
    border-right: 1px solid #334155;
}
QFrame#card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
}
QFrame#statCard {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
}
QLabel#appTitle {
    font-size: 20px;
    font-weight: 700;
    color: #f8fafc;
}
QLabel#sectionTitle {
    font-size: 18px;
    font-weight: 600;
    color: #f1f5f9;
}
QLabel#subtitle {
    color: #94a3b8;
    font-size: 13px;
}
QLabel#timerLabel {
    font-size: 22px;
    font-weight: 700;
    color: #38bdf8;
}
QLabel#timerWarning {
    color: #f87171;
}
QPushButton {
    background-color: #334155;
    color: #f8fafc;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #475569;
}
QPushButton:pressed {
    background-color: #1e293b;
}
QPushButton#primaryBtn {
    background-color: #2563eb;
    color: white;
    font-size: 15px;
    padding: 14px 28px;
    border-radius: 10px;
}
QPushButton#primaryBtn:hover {
    background-color: #1d4ed8;
}
QPushButton#dangerBtn {
    background-color: #dc2626;
}
QPushButton#dangerBtn:hover {
    background-color: #b91c1c;
}
QPushButton#navBtn {
    text-align: left;
    padding: 12px 16px;
    border-radius: 8px;
    background-color: transparent;
    color: #cbd5e1;
}
QPushButton#navBtn:hover {
    background-color: #334155;
}
QPushButton#navBtn[active="true"] {
    background-color: #2563eb;
    color: white;
}
QLineEdit, QSpinBox, QComboBox {
    background-color: #0f172a;
    border: 1px solid #475569;
    border-radius: 8px;
    padding: 10px 12px;
    color: #f8fafc;
    min-height: 20px;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #1e293b;
    color: #f8fafc;
    selection-background-color: #2563eb;
}
QProgressBar {
    border: none;
    border-radius: 6px;
    background-color: #334155;
    text-align: center;
    color: white;
    height: 10px;
}
QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 6px;
}
QRadioButton {
    spacing: 10px;
    padding: 10px;
    border-radius: 8px;
}
QRadioButton:hover {
    background-color: #1e293b;
}
QRadioButton:checked {
    background-color: #1e3a5f;
    border: 1px solid #2563eb;
    border-radius: 8px;
}
QTableWidget {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    gridline-color: #334155;
}
QTableWidget::item {
    padding: 8px;
}
QHeaderView::section {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 10px;
    border: none;
    font-weight: 600;
}
QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:vertical {
    background: #1e293b;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #475569;
    border-radius: 5px;
    min-height: 30px;
}
"""

LIGHT_THEME = """
QMainWindow, QWidget {
    background-color: #f8fafc;
    color: #0f172a;
    font-family: "Segoe UI", sans-serif;
    font-size: 14px;
}
QFrame#sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}
QFrame#card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}
QFrame#statCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
}
QLabel#appTitle {
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
}
QLabel#sectionTitle {
    font-size: 18px;
    font-weight: 600;
}
QLabel#subtitle {
    color: #64748b;
}
QLabel#timerLabel {
    font-size: 22px;
    font-weight: 700;
    color: #2563eb;
}
QPushButton {
    background-color: #e2e8f0;
    color: #0f172a;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #cbd5e1;
}
QPushButton#primaryBtn {
    background-color: #2563eb;
    color: white;
}
QPushButton#primaryBtn:hover {
    background-color: #1d4ed8;
}
QPushButton#navBtn {
    text-align: left;
    padding: 12px 16px;
    border-radius: 8px;
    background-color: transparent;
}
QPushButton#navBtn:hover {
    background-color: #f1f5f9;
}
QPushButton#navBtn[active="true"] {
    background-color: #2563eb;
    color: white;
}
QLineEdit, QSpinBox, QComboBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px 12px;
}
QProgressBar {
    border: none;
    border-radius: 6px;
    background-color: #e2e8f0;
    height: 10px;
}
QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 6px;
}
QRadioButton:checked {
    background-color: #eff6ff;
    border: 1px solid #2563eb;
    border-radius: 8px;
}
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}
QHeaderView::section {
    background-color: #f1f5f9;
    color: #475569;
    padding: 10px;
    border: none;
}
"""


def get_theme_stylesheet(theme: str) -> str:
    return LIGHT_THEME if theme == "light" else DARK_THEME
