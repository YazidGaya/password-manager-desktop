# Boîtes de dialogue utilisées dans l'application.
from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from ..services import Entry, VaultService


class EntryDialog(QDialog):
    def __init__(self, vault_service: VaultService, parent=None, entry: Optional[Entry] = None) -> None:
        super().__init__(parent)
        self.vault_service = vault_service
        self.entry = entry
        self._password_visible = False
        self.setWindowTitle("Ajouter une entrée" if entry is None else "Modifier l'entrée")
        self.setModal(True)
        self.resize(560, 620)

        self.service_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self.update_password_strength)
        self.category_input = QLineEdit()
        self.website_input = QLineEdit()
        self.notes_input = QTextEdit()
        self.notes_input.setMinimumHeight(120)
        self.length_input = QSpinBox()
        self.length_input.setRange(8, 64)
        self.length_input.setValue(20)
        self.symbols_checkbox = QCheckBox("Inclure des symboles")
        self.symbols_checkbox.setChecked(True)

        outer = QVBoxLayout()
        outer.setContentsMargins(18, 18, 18, 18)

        hero = QFrame()
        hero.setObjectName("dialogHeroCard")
        hero_title = QLabel("Nouvelle entrée" if entry is None else "Modifier l'entrée")
        hero_title.setObjectName("titleLabel")
        hero_subtitle = QLabel("Protégez vos accès dans un coffre local chiffré.")
        hero_subtitle.setObjectName("subtitleLabel")
        hero_layout = QVBoxLayout()
        hero_layout.setContentsMargins(22, 20, 22, 20)
        hero_layout.addWidget(hero_title)
        hero_layout.addWidget(hero_subtitle)
        hero.setLayout(hero_layout)

        card = QFrame()
        card.setObjectName("dialogCard")

        title = QLabel("Détails de l'entrée")
        title.setObjectName("sectionTitle")
        hint = QLabel("Renseignez les champs puis enregistrez. Vous pouvez générer un mot de passe fort avant la sauvegarde.")
        hint.setObjectName("mutedLabel")

        password_layout = QHBoxLayout()
        password_layout.setSpacing(10)
        password_layout.addWidget(self.password_input, 1)
        self.eye_button = QPushButton("👁")
        self.eye_button.setObjectName("eyeButton")
        self.eye_button.setProperty("secondary", True)
        self.eye_button.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.eye_button)

        form = QFormLayout()
        form.setSpacing(12)
        form.addRow("Service", self.service_input)
        form.addRow("Identifiant ou email", self.username_input)
        form.addRow("Mot de passe", password_layout)
        form.addRow("Catégorie", self.category_input)
        form.addRow("Site web", self.website_input)
        form.addRow("Notes", self.notes_input)

        self.strength_label = QLabel("Force du mot de passe")
        self.strength_label.setObjectName("mutedLabel")
        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(False)

        generator_card = QFrame()
        generator_card.setObjectName("miniStatCard")
        generator_layout = QHBoxLayout()
        generator_layout.setContentsMargins(16, 14, 16, 14)
        generator_layout.addWidget(QLabel("Longueur"))
        generator_layout.addWidget(self.length_input)
        generator_layout.addWidget(self.symbols_checkbox)
        generator_layout.addStretch()
        generator_btn = QPushButton("⚡ Générer")
        generator_btn.setProperty("secondary", True)
        generator_btn.clicked.connect(self.generate_password)
        generator_layout.addWidget(generator_btn)
        generator_card.setLayout(generator_layout)

        buttons = QHBoxLayout()
        save_btn = QPushButton("Enregistrer")
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setProperty("secondary", True)
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 22, 22, 22)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addSpacing(12)
        layout.addLayout(form)
        layout.addWidget(self.strength_label)
        layout.addWidget(self.strength_bar)
        layout.addSpacing(8)
        layout.addWidget(generator_card)
        layout.addSpacing(12)
        layout.addLayout(buttons)
        card.setLayout(layout)

        outer.addWidget(hero)
        outer.addSpacing(12)
        outer.addWidget(card)
        self.setLayout(outer)

        for widget, blur, alpha in [(hero, 38, 95), (card, 34, 90)]:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(blur)
            shadow.setOffset(0, 10)
            shadow.setColor(QColor(0, 0, 0, alpha))
            widget.setGraphicsEffect(shadow)

        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(220)
        self._anim.setStartValue(0.94)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.start()

        if entry:
            self.service_input.setText(entry.service_name)
            self.username_input.setText(entry.username)
            self.password_input.setText(entry.password)
            self.category_input.setText(entry.category)
            self.website_input.setText(entry.website)
            self.notes_input.setPlainText(entry.notes)
            self.update_password_strength(entry.password)

    # Ce bouton affiche ou masque le mot de passe courant.
    def toggle_password_visibility(self) -> None:
        self._password_visible = not self._password_visible
        self.password_input.setEchoMode(QLineEdit.Normal if self._password_visible else QLineEdit.Password)
        self.eye_button.setText("🙈" if self._password_visible else "👁")

    # Cette méthode demande au service de générer un mot de passe fort.
    def generate_password(self) -> None:
        try:
            password = self.vault_service.generate_suggested_password(
                length=self.length_input.value(),
                use_symbols=self.symbols_checkbox.isChecked(),
            )
            self.password_input.setText(password)
        except Exception as exc:
            QMessageBox.warning(self, "Erreur", str(exc))

    # Donne un retour visuel rapide sur la force du mot de passe.
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

    # Prépare les données envoyées à la couche de services pour l'enregistrement.
    def get_payload(self) -> dict:
        return {
            "service_name": self.service_input.text().strip(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text(),
            "category": self.category_input.text().strip(),
            "website": self.website_input.text().strip(),
            "notes": self.notes_input.toPlainText().strip(),
        }
