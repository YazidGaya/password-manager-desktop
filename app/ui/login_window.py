# Fenêtre de connexion au coffre SafePass.
from __future__ import annotations

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..services import VaultService


class LoginWindow(QWidget):
    def __init__(self, vault_service: VaultService, on_success) -> None:
        super().__init__()
        self.vault_service = vault_service
        self.on_success = on_success
        self._password_visible = False
        self.setWindowTitle("Connexion au coffre")
        self.resize(560, 420)

        outer = QVBoxLayout()
        outer.setContentsMargins(26, 26, 26, 26)

        hero = QFrame()
        hero.setObjectName("dialogHeroCard")
        self.title = QLabel("Bienvenue dans SafePass")
        self.title.setObjectName("titleLabel")
        self.subtitle = QLabel("Déverrouillez votre coffre local avec votre mot de passe maître.")
        self.subtitle.setObjectName("subtitleLabel")
        hero_layout = QVBoxLayout()
        hero_layout.setContentsMargins(22, 20, 22, 20)
        hero_layout.addWidget(self.title)
        hero_layout.addWidget(self.subtitle)
        hero.setLayout(hero_layout)

        card = QFrame()
        card.setObjectName("dialogCard")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe maître")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.handle_login)

        password_layout = QHBoxLayout()
        password_layout.setSpacing(10)
        password_layout.addWidget(self.password_input, 1)
        self.eye_button = QPushButton("👁")
        self.eye_button.setObjectName("eyeButton")
        self.eye_button.setProperty("secondary", True)
        self.eye_button.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.eye_button)

        login_btn = QPushButton("Déverrouiller")
        login_btn.clicked.connect(self.handle_login)

        helper = QLabel("Après connexion, toutes les données sont déchiffrées en mémoire uniquement pendant la session.")
        helper.setObjectName("mutedLabel")

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(QLabel("Mot de passe maître"))
        layout.addLayout(password_layout)
        layout.addSpacing(10)
        layout.addWidget(helper)
        layout.addSpacing(16)
        layout.addWidget(login_btn)
        card.setLayout(layout)

        outer.addWidget(hero)
        outer.addSpacing(12)
        outer.addWidget(card)
        self.setLayout(outer)

        for widget, blur, alpha in [(hero, 36, 95), (card, 34, 90)]:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(blur)
            shadow.setOffset(0, 10)
            shadow.setColor(QColor(0, 0, 0, alpha))
            widget.setGraphicsEffect(shadow)

        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(240)
        self._anim.setStartValue(0.92)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.start()

    # Ce bouton affiche ou masque le champ du mot de passe maître.
    def toggle_password_visibility(self) -> None:
        self._password_visible = not self._password_visible
        self.password_input.setEchoMode(QLineEdit.Normal if self._password_visible else QLineEdit.Password)
        self.eye_button.setText("🙈" if self._password_visible else "👁")

    # Valide le mot de passe maître puis ouvre la fenêtre principale.
    def handle_login(self) -> None:
        try:
            email = self.vault_service.login(self.password_input.text())
            self.on_success(email)
            self.close()
        except Exception as exc:
            QMessageBox.warning(self, "Échec de connexion", str(exc))
