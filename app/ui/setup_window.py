# Fenêtre d'initialisation du coffre SafePass.
from __future__ import annotations

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..services import VaultService


class SetupWindow(QWidget):
    def __init__(self, vault_service: VaultService, on_success) -> None:
        super().__init__()
        self.vault_service = vault_service
        self.on_success = on_success
        self._password_visible = False
        self._confirm_visible = False
        self.setWindowTitle("Initialisation du coffre")
        self.resize(600, 500)

        outer = QVBoxLayout()
        outer.setContentsMargins(24, 24, 24, 24)

        hero = QFrame()
        hero.setObjectName("dialogHeroCard")
        self.title = QLabel("Créer votre coffre-fort")
        self.title.setObjectName("titleLabel")
        self.subtitle = QLabel("Choisissez un email et un mot de passe maître robuste pour protéger vos données.")
        self.subtitle.setObjectName("subtitleLabel")
        hero_layout = QVBoxLayout()
        hero_layout.setContentsMargins(22, 20, 22, 20)
        hero_layout.addWidget(self.title)
        hero_layout.addWidget(self.subtitle)
        hero.setLayout(hero_layout)

        card = QFrame()
        card.setObjectName("dialogCard")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("exemple@domaine.com")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe maître")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self.update_password_strength)
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirmer le mot de passe")
        self.confirm_input.setEchoMode(QLineEdit.Password)

        password_layout = QHBoxLayout()
        password_layout.setSpacing(10)
        password_layout.addWidget(self.password_input, 1)
        self.password_eye = QPushButton("👁")
        self.password_eye.setObjectName("eyeButton")
        self.password_eye.setProperty("secondary", True)
        self.password_eye.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.password_eye)

        confirm_layout = QHBoxLayout()
        confirm_layout.setSpacing(10)
        confirm_layout.addWidget(self.confirm_input, 1)
        self.confirm_eye = QPushButton("👁")
        self.confirm_eye.setObjectName("eyeButton")
        self.confirm_eye.setProperty("secondary", True)
        self.confirm_eye.clicked.connect(self.toggle_confirm_visibility)
        confirm_layout.addWidget(self.confirm_eye)

        form = QFormLayout()
        form.setSpacing(12)
        form.addRow("Email", self.email_input)
        form.addRow("Mot de passe maître", password_layout)
        form.addRow("Confirmation", confirm_layout)

        self.strength_label = QLabel("Force du mot de passe")
        self.strength_label.setObjectName("mutedLabel")
        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(False)

        submit_btn = QPushButton("Créer le coffre")
        submit_btn.clicked.connect(self.handle_submit)

        helper = QLabel("Conseil  utilisez une phrase longue avec lettres, chiffres et symboles.")
        helper.setObjectName("mutedLabel")

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addLayout(form)
        layout.addSpacing(8)
        layout.addWidget(self.strength_label)
        layout.addWidget(self.strength_bar)
        layout.addWidget(helper)
        layout.addSpacing(14)
        layout.addWidget(submit_btn)
        card.setLayout(layout)

        outer.addWidget(hero)
        outer.addSpacing(12)
        outer.addWidget(card)
        self.setLayout(outer)

        for widget, blur, alpha in [(hero, 42, 95), (card, 36, 85)]:
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

    # Ce bouton affiche ou masque le premier champ de mot de passe.
    def toggle_password_visibility(self) -> None:
        self._password_visible = not self._password_visible
        self.password_input.setEchoMode(QLineEdit.Normal if self._password_visible else QLineEdit.Password)
        self.password_eye.setText("🙈" if self._password_visible else "👁")

    # Ce bouton affiche ou masque le champ de confirmation.
    def toggle_confirm_visibility(self) -> None:
        self._confirm_visible = not self._confirm_visible
        self.confirm_input.setEchoMode(QLineEdit.Normal if self._confirm_visible else QLineEdit.Password)
        self.confirm_eye.setText("🙈" if self._confirm_visible else "👁")

    # Met à jour la barre de progression qui estime la qualité du mot de passe.
    def update_password_strength(self, password: str) -> None:
        score = 0
        if len(password) >= 8:
            score += 20
        if len(password) >= 12:
            score += 15
        if any(char.islower() for char in password):
            score += 15
        if any(char.isupper() for char in password):
            score += 15
        if any(char.isdigit() for char in password):
            score += 15
        if any(not char.isalnum() for char in password):
            score += 20
        score = min(score, 100)
        self.strength_bar.setValue(score)

        if score < 45:
            self.strength_label.setText("Force du mot de passe  Faible")
            self.strength_label.setObjectName("strengthWeak")
        elif score < 75:
            self.strength_label.setText("Force du mot de passe  Moyenne")
            self.strength_label.setObjectName("strengthMedium")
        else:
            self.strength_label.setText("Force du mot de passe  Forte")
            self.strength_label.setObjectName("strengthStrong")
        self.strength_label.style().unpolish(self.strength_label)
        self.strength_label.style().polish(self.strength_label)

    # Crée le coffre après les validations de base.
    def handle_submit(self) -> None:
        try:
            self.vault_service.setup_vault(
                self.email_input.text(),
                self.password_input.text(),
                self.confirm_input.text(),
            )
            QMessageBox.information(self, "Succès", "Le coffre a été créé avec succès.")
            self.on_success()
            self.close()
        except Exception as exc:
            QMessageBox.warning(self, "Erreur", str(exc))
