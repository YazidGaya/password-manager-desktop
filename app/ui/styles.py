# Feuille de style globale de toute l'application.
APP_STYLESHEET = """
QWidget {
    background-color: #0b1020;
    color: #ecf2ff;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #0b1020;
}

QFrame#pageCard {
    background: transparent;
    border: none;
}

QFrame#heroCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1b2a52, stop:0.55 #243f7c, stop:1 #4d2f7d);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 26px;
}

QFrame#dialogHeroCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #18284f, stop:1 #3b2f73);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 24px;
}

QFrame#sidebarCard {
    background-color: rgba(17, 24, 39, 0.96);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 24px;
}

QFrame#sectionCard, QFrame#toolbarCard, QFrame#dialogCard, QFrame#statsCard, QFrame#detailCard {
    background-color: rgba(16, 23, 40, 0.96);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 22px;
}

QFrame#miniStatCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(44, 84, 172, 0.28), stop:1 rgba(117, 77, 196, 0.22));
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
}


QLabel {
    background: transparent;
}

QLabel#titleLabel {
    font-size: 29px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#subtitleLabel {
    color: rgba(255, 255, 255, 0.78);
    font-size: 13px;
}

QLabel#sectionTitle {
    font-size: 18px;
    font-weight: 650;
    color: #ffffff;
}

QLabel#mutedLabel {
    color: #93a3c4;
    font-size: 12px;
}

QLabel#chipLabel {
    background-color: rgba(255, 255, 255, 0.08);
    color: #f5f8ff;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 7px 12px;
    font-weight: 600;
}

QLabel#sidebarBrand {
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#sidebarLabel {
    color: #8fa2c9;
    font-size: 12px;
    font-weight: 600;
}

QLabel#sidebarValue {
    color: #ffffff;
    font-size: 14px;
    font-weight: 600;
}

QLabel#statNumber {
    font-size: 27px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#statCaption {
    color: #90a4c8;
    font-size: 12px;
}

QLabel#detailTitle {
    color: #b4c5e6;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
}

QLabel#detailValue {
    color: #ffffff;
    font-size: 13px;
}

QLabel#strengthWeak {
    color: #ff8f8f;
    font-weight: 600;
}

QLabel#strengthMedium {
    color: #ffd38a;
    font-weight: 600;
}

QLabel#strengthStrong {
    color: #9ce2b0;
    font-weight: 600;
}

QLineEdit, QTextEdit, QSpinBox, QComboBox {
    background-color: rgba(7, 12, 23, 0.9);
    color: #f4f7ff;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 14px;
    padding: 10px 12px;
    selection-background-color: #4f86ff;
}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #5b8cff;
    background-color: rgba(10, 18, 34, 0.98);
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4f7cff, stop:1 #6b4dff);
    color: white;
    font-weight: 650;
    border: none;
    border-radius: 14px;
    padding: 10px 16px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5a86ff, stop:1 #795eff);
}

QPushButton:pressed {
    padding-top: 11px;
    padding-bottom: 9px;
}

QPushButton[secondary="true"] {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.07);
}

QPushButton[secondary="true"]:hover {
    background: rgba(255, 255, 255, 0.12);
}

QPushButton[danger="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #d44f6b, stop:1 #a83057);
}

QPushButton[danger="true"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #e05d79, stop:1 #b93d65);
}

QPushButton[nav="true"] {
    text-align: left;
    padding: 12px 14px;
    border-radius: 16px;
    background: transparent;
    border: 1px solid transparent;
    color: #d8e3ff;
}

QPushButton[nav="true"]:hover {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.06);
}

QPushButton[navActive="true"] {
    background: rgba(95, 134, 255, 0.18);
    border: 1px solid rgba(95, 134, 255, 0.26);
}

QPushButton#eyeButton {
    min-width: 44px;
    max-width: 44px;
    padding: 9px;
}

QTableWidget {
    background-color: rgba(10, 15, 28, 0.92);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 18px;
    gridline-color: transparent;
    alternate-background-color: rgba(255, 255, 255, 0.03);
    selection-background-color: rgba(89, 130, 255, 0.28);
}

QHeaderView::section {
    background: transparent;
    color: #a9bde3;
    font-size: 12px;
    font-weight: 650;
    border: none;
    padding: 12px 10px;
}

QTableWidget::item {
    padding: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

QTableCornerButton::section {
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    background: transparent;
    width: 12px;
    margin: 6px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.14);
    border-radius: 6px;
    min-height: 26px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QProgressBar {
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    text-align: center;
    color: #ffffff;
    min-height: 12px;
}

QProgressBar::chunk {
    border-radius: 9px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4f7cff, stop:1 #7b61ff);
}

QCheckBox {
    spacing: 10px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:unchecked {
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: rgba(0, 0, 0, 0.15);
}

QCheckBox::indicator:checked {
    border-radius: 6px;
    border: 1px solid #628cff;
    background: #628cff;
}

QMessageBox {
    background-color: #12192b;
}
"""
