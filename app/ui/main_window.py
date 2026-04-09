# Fenêtre principale de gestion du coffre et des identifiants.
from __future__ import annotations

from pathlib import Path
from typing import List

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QTimer, Qt
from PyQt5.QtGui import QColor, QGuiApplication
from PyQt5.QtWidgets import (
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..config import SESSION_IDLE_MINUTES
from ..services import Entry, VaultService
from .dialogs import EntryDialog


class MainWindow(QMainWindow):
    def __init__(self, vault_service: VaultService, user_email: str, on_logout) -> None:
        super().__init__()
        self.vault_service = vault_service
        self.user_email = user_email
        self.on_logout = on_logout
        self.entries: List[Entry] = []
        self.filtered_entries: List[Entry] = []
        self.setWindowTitle("SafePass - Coffre-fort")
        self.resize(1280, 760)

        central = QWidget()
        self.setCentralWidget(central)

        shell = QHBoxLayout()
        shell.setContentsMargins(18, 18, 18, 18)
        shell.setSpacing(16)

        # La barre latérale regroupe les actions globales et les informations rapides du compte.
        sidebar = QFrame()
        sidebar.setObjectName("sidebarCard")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(18, 18, 18, 18)
        sidebar_layout.setSpacing(10)

        brand = QLabel("SafePass")
        brand.setObjectName("sidebarBrand")
        welcome = QLabel("Gestionnaire local sécurisé")
        welcome.setObjectName("mutedLabel")

        user_label = QLabel("Compte")
        user_label.setObjectName("sidebarLabel")
        user_value = QLabel(self.user_email)
        user_value.setObjectName("sidebarValue")

        self.sidebar_total = QLabel("0")
        self.sidebar_total.setObjectName("statNumber")
        self.sidebar_total_caption = QLabel("Entrées stockées")
        self.sidebar_total_caption.setObjectName("statCaption")

        self.sidebar_categories = QLabel("0")
        self.sidebar_categories.setObjectName("statNumber")
        self.sidebar_categories_caption = QLabel("Catégories")
        self.sidebar_categories_caption.setObjectName("statCaption")

        add_btn = QPushButton("➕ Nouvelle entrée")
        add_btn.setProperty("nav", True)
        add_btn.setProperty("navActive", True)
        generate_btn = QPushButton("⚡ Générer un mot de passe")
        generate_btn.setProperty("nav", True)
        export_btn = QPushButton("📤 Exporter le coffre")
        export_btn.setProperty("nav", True)
        import_btn = QPushButton("📥 Importer un coffre")
        import_btn.setProperty("nav", True)
        lock_btn = QPushButton("🔒 Verrouiller la session")
        lock_btn.setProperty("nav", True)

        add_btn.clicked.connect(self.add_entry)
        generate_btn.clicked.connect(self.open_generator_dialog)
        export_btn.clicked.connect(self.export_entries)
        import_btn.clicked.connect(self.import_entries)
        lock_btn.clicked.connect(self.logout)

        stat_one = self._build_sidebar_stat_card(self.sidebar_total, self.sidebar_total_caption)
        stat_two = self._build_sidebar_stat_card(self.sidebar_categories, self.sidebar_categories_caption)

        sidebar_layout.addWidget(brand)
        sidebar_layout.addWidget(welcome)
        sidebar_layout.addSpacing(18)
        sidebar_layout.addWidget(user_label)
        sidebar_layout.addWidget(user_value)
        sidebar_layout.addSpacing(18)
        sidebar_layout.addWidget(stat_one)
        sidebar_layout.addWidget(stat_two)
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(add_btn)
        sidebar_layout.addWidget(generate_btn)
        sidebar_layout.addWidget(export_btn)
        sidebar_layout.addWidget(import_btn)
        sidebar_layout.addWidget(lock_btn)
        sidebar_layout.addStretch()
        sidebar.setLayout(sidebar_layout)

        # La zone principale contient le tableau et le détail de l'entrée sélectionnée.
        page_card = QFrame()
        page_card.setObjectName("pageCard")
        page_layout = QVBoxLayout()
        page_layout.setSpacing(12)

        hero_card = QFrame()
        hero_card.setObjectName("heroCard")
        header_title = QLabel("Tableau de bord")
        header_title.setObjectName("titleLabel")
        header_subtitle = QLabel(f"Coffre local sécurisé  connecté en tant que {user_email}")
        header_subtitle.setObjectName("subtitleLabel")
        self.count_chip = QLabel("0 entrées")
        self.count_chip.setObjectName("chipLabel")
        self.category_chip = QLabel("0 catégories")
        self.category_chip.setObjectName("chipLabel")
        self.search_chip = QLabel("Recherche inactive")
        self.search_chip.setObjectName("chipLabel")

        chips_layout = QHBoxLayout()
        chips_layout.addWidget(self.count_chip)
        chips_layout.addWidget(self.category_chip)
        chips_layout.addWidget(self.search_chip)
        chips_layout.addStretch()

        hero_layout = QVBoxLayout()
        hero_layout.setContentsMargins(24, 22, 24, 22)
        hero_layout.addWidget(header_title)
        hero_layout.addWidget(header_subtitle)
        hero_layout.addSpacing(8)
        hero_layout.addLayout(chips_layout)
        hero_card.setLayout(hero_layout)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        self.visible_count_value = QLabel("0")
        self.visible_count_value.setObjectName("statNumber")
        self.visible_count_caption = QLabel("Entrées visibles")
        self.visible_count_caption.setObjectName("statCaption")
        self.website_count_value = QLabel("0")
        self.website_count_value.setObjectName("statNumber")
        self.website_count_caption = QLabel("Sites renseignés")
        self.website_count_caption.setObjectName("statCaption")
        self.note_count_value = QLabel("0")
        self.note_count_value.setObjectName("statNumber")
        self.note_count_caption = QLabel("Notes présentes")
        self.note_count_caption.setObjectName("statCaption")
        stats_row.addWidget(self._build_stat_card(self.visible_count_value, self.visible_count_caption))
        stats_row.addWidget(self._build_stat_card(self.website_count_value, self.website_count_caption))
        stats_row.addWidget(self._build_stat_card(self.note_count_value, self.note_count_caption))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un service, un identifiant, une catégorie ou un site")
        self.search_input.textChanged.connect(self.refresh_table)

        self.table = QTableWidget(0, 6)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setHorizontalHeaderLabels(["ID", "Service", "Identifiant", "Catégorie", "Site web", "Modifié le"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_selected_entry)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnHidden(0, True)
        self.table.itemSelectionChanged.connect(self.update_details_panel)

        toolbar_card = QFrame()
        toolbar_card.setObjectName("toolbarCard")
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(14, 14, 14, 14)
        toolbar.setSpacing(10)

        add_small_btn = QPushButton("Ajouter")
        edit_btn = QPushButton("Modifier")
        delete_btn = QPushButton("Supprimer")
        delete_btn.setProperty("danger", True)
        copy_user_btn = QPushButton("Copier identifiant")
        copy_pwd_btn = QPushButton("Copier mot de passe")
        clear_btn = QPushButton("Effacer la recherche")
        clear_btn.setProperty("secondary", True)

        add_small_btn.clicked.connect(self.add_entry)
        edit_btn.clicked.connect(self.edit_selected_entry)
        delete_btn.clicked.connect(self.delete_selected_entry)
        copy_user_btn.clicked.connect(self.copy_selected_username)
        copy_pwd_btn.clicked.connect(self.copy_selected_password)
        clear_btn.clicked.connect(self.search_input.clear)

        for widget in [add_small_btn, edit_btn, delete_btn, copy_user_btn, copy_pwd_btn, clear_btn]:
            toolbar.addWidget(widget)
        toolbar.addStretch()
        toolbar_card.setLayout(toolbar)

        content_card = QFrame()
        content_card.setObjectName("sectionCard")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_title = QLabel("Vos identifiants enregistrés")
        content_title.setObjectName("sectionTitle")
        content_hint = QLabel("Double cliquez sur une ligne pour la modifier. Les données restent chiffrées au repos dans SQLite.")
        content_hint.setObjectName("mutedLabel")
        content_layout.addWidget(content_title)
        content_layout.addWidget(content_hint)
        content_layout.addSpacing(8)
        content_layout.addWidget(self.search_input)
        content_layout.addSpacing(8)
        content_layout.addWidget(toolbar_card)
        content_layout.addSpacing(8)
        content_layout.addWidget(self.table)
        content_card.setLayout(content_layout)

        # Le panneau de détail affiche plus clairement l'entrée actuellement sélectionnée.
        detail_card = QFrame()
        detail_card.setObjectName("detailCard")
        detail_layout = QVBoxLayout()
        detail_layout.setContentsMargins(20, 20, 20, 20)
        detail_layout.setSpacing(10)
        detail_title = QLabel("Détail de l'entrée")
        detail_title.setObjectName("sectionTitle")
        detail_hint = QLabel("Sélectionnez une ligne dans le tableau pour afficher son contenu.")
        detail_hint.setObjectName("mutedLabel")

        self.detail_service = self._build_detail_pair("Service")
        self.detail_username = self._build_detail_pair("Identifiant")
        self.detail_password = self._build_detail_pair("Mot de passe")
        self.detail_category = self._build_detail_pair("Catégorie")
        self.detail_website = self._build_detail_pair("Site web")
        self.detail_updated = self._build_detail_pair("Dernière modification")

        self.notes_view = QTextEdit()
        self.notes_view.setReadOnly(True)
        self.notes_view.setPlaceholderText("Aucune note pour cette entrée")
        self.notes_view.setMinimumHeight(140)

        detail_layout.addWidget(detail_title)
        detail_layout.addWidget(detail_hint)
        detail_layout.addWidget(self.detail_service[0])
        detail_layout.addWidget(self.detail_username[0])
        detail_layout.addWidget(self.detail_password[0])
        detail_layout.addWidget(self.detail_category[0])
        detail_layout.addWidget(self.detail_website[0])
        detail_layout.addWidget(self.detail_updated[0])
        detail_layout.addWidget(QLabel("Notes"))
        detail_layout.addWidget(self.notes_view)
        detail_card.setLayout(detail_layout)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)
        bottom_row.addWidget(content_card, 3)
        bottom_row.addWidget(detail_card, 2)

        page_layout.addWidget(hero_card)
        page_layout.addLayout(stats_row)
        page_layout.addLayout(bottom_row)
        page_card.setLayout(page_layout)

        shell.addWidget(sidebar)
        shell.addWidget(page_card, 1)
        central.setLayout(shell)

        self._add_shadow(sidebar, blur=30, offset=0, alpha=60)
        self._add_shadow(hero_card, blur=40, offset=0, alpha=85)
        self._add_shadow(content_card, blur=32, offset=0, alpha=65)
        self._add_shadow(detail_card, blur=32, offset=0, alpha=65)
        self._add_shadow(toolbar_card, blur=24, offset=0, alpha=40)
        self._fade_in()

        # Le minuteur d'inactivité verrouille l'application après un certain délai.
        self._idle_timer = QTimer(self)
        self._idle_timer.setInterval(SESSION_IDLE_MINUTES * 60 * 1000)
        self._idle_timer.timeout.connect(self.logout_due_to_idle)
        self._idle_timer.start()

        self.refresh_entries()

    # Cette méthode utilitaire construit une carte statistique compacte pour le tableau de bord.
    def _build_stat_card(self, number_label: QLabel, caption_label: QLabel) -> QFrame:
        card = QFrame()
        card.setObjectName("miniStatCard")
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 16, 18, 16)
        layout.addWidget(number_label)
        layout.addWidget(caption_label)
        card.setLayout(layout)
        return card

    # Cette méthode utilitaire construit une carte statistique compacte pour la barre latérale.
    def _build_sidebar_stat_card(self, number_label: QLabel, caption_label: QLabel) -> QFrame:
        card = QFrame()
        card.setObjectName("statsCard")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 14, 16, 14)
        layout.addWidget(number_label)
        layout.addWidget(caption_label)
        card.setLayout(layout)
        return card

    # Cette méthode utilitaire crée une paire de libellés pour le panneau de détail.
    def _build_detail_pair(self, title: str):
        wrapper = QFrame()
        wrapper.setObjectName("statsCard")
        layout = QVBoxLayout()
        layout.setContentsMargins(14, 12, 14, 12)
        key = QLabel(title)
        key.setObjectName("detailTitle")
        value = QLabel("-")
        value.setObjectName("detailValue")
        value.setWordWrap(True)
        layout.addWidget(key)
        layout.addWidget(value)
        wrapper.setLayout(layout)
        return wrapper, value

    # Applique une ombre légère pour mieux faire ressortir les cartes.
    def _add_shadow(self, widget, blur=30, offset=0, alpha=80) -> None:
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(blur)
        shadow.setOffset(offset, 8 if offset == 0 else offset)
        shadow.setColor(QColor(0, 0, 0, alpha))
        widget.setGraphicsEffect(shadow)

    # Ajoute une ouverture plus fluide à la fenêtre.
    def _fade_in(self) -> None:
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(260)
        self._anim.setStartValue(0.92)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.start()

    # Réinitialise le minuteur d'inactivité à chaque interaction utilisateur.
    def reset_idle_timer(self) -> None:
        self._idle_timer.start()

    def mousePressEvent(self, event):
        self.reset_idle_timer()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        self.reset_idle_timer()
        super().keyPressEvent(event)

    # Charge toutes les entrées depuis le service et met à jour le tableau de bord.
    def refresh_entries(self) -> None:
        try:
            self.entries = self.vault_service.list_entries()
            category_count = len({e.category for e in self.entries if e.category})
            self.count_chip.setText(f"{len(self.entries)} entrée(s)")
            self.category_chip.setText(f"{category_count} catégorie(s)")
            self.sidebar_total.setText(str(len(self.entries)))
            self.sidebar_categories.setText(str(category_count))
            self.refresh_table()
        except Exception as exc:
            QMessageBox.warning(self, "Erreur", str(exc))

    # Filtre les entrées selon la recherche courante puis rafraîchit le tableau.
    def refresh_table(self) -> None:
        query = self.search_input.text().strip().lower()
        if query:
            self.filtered_entries = [
                entry for entry in self.entries
                if query in entry.service_name.lower()
                or query in entry.username.lower()
                or query in entry.category.lower()
                or query in entry.website.lower()
                or query in entry.notes.lower()
            ]
            self.search_chip.setText(f"Recherche  {len(self.filtered_entries)} résultat(s)")
        else:
            self.filtered_entries = list(self.entries)
            self.search_chip.setText("Recherche inactive")

        self.table.setRowCount(len(self.filtered_entries))
        for row_idx, entry in enumerate(self.filtered_entries):
            values = [
                str(entry.id),
                entry.service_name,
                entry.username,
                entry.category,
                entry.website,
                entry.updated_at,
            ]
            for col_idx, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col_idx != 0:
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(row_idx, col_idx, item)
        self.table.resizeColumnsToContents()

        self.visible_count_value.setText(str(len(self.filtered_entries)))
        self.website_count_value.setText(str(sum(1 for entry in self.filtered_entries if entry.website.strip())))
        self.note_count_value.setText(str(sum(1 for entry in self.filtered_entries if entry.notes.strip())))

        if self.filtered_entries:
            self.table.selectRow(0)
        else:
            self.clear_details_panel()

    # Retourne l'identifiant en base de la ligne sélectionnée.
    def _selected_entry_id(self):
        items = self.table.selectedItems()
        if not items:
            return None
        return int(self.table.item(items[0].row(), 0).text())

    # Retourne l'objet complet correspondant à l'entrée sélectionnée.
    def _selected_entry(self) -> Entry | None:
        entry_id = self._selected_entry_id()
        if entry_id is None:
            return None
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    # Ouvre la fenêtre pour créer un nouvel identifiant stocké.
    def add_entry(self) -> None:
        dialog = EntryDialog(self.vault_service, self)
        if dialog.exec_():
            try:
                self.vault_service.create_entry(**dialog.get_payload())
                self.refresh_entries()
                QMessageBox.information(self, "Succès", "Entrée ajoutée avec succès.")
            except Exception as exc:
                QMessageBox.warning(self, "Erreur", str(exc))

    # Ouvre la fenêtre du générateur et l'utilise uniquement pour générer un mot de passe.
    def open_generator_dialog(self) -> None:
        dialog = EntryDialog(self.vault_service, self)
        dialog.service_input.setPlaceholderText("Facultatif")
        dialog.username_input.setPlaceholderText("Facultatif")
        dialog.service_input.setText("Générateur rapide")
        if dialog.exec_():
            app_instance = QGuiApplication.instance()
            if app_instance is not None:
                app_instance.clipboard().setText(dialog.password_input.text())
            QMessageBox.information(self, "Copié", "Le mot de passe généré a été copié dans le presse papiers.")

    # Modifie l'entrée actuellement sélectionnée.
    def edit_selected_entry(self) -> None:
        entry = self._selected_entry()
        if not entry:
            QMessageBox.information(self, "Information", "Veuillez sélectionner une entrée.")
            return
        dialog = EntryDialog(self.vault_service, self, entry=entry)
        if dialog.exec_():
            try:
                self.vault_service.update_entry(entry.id, **dialog.get_payload())
                self.refresh_entries()
                QMessageBox.information(self, "Succès", "Entrée modifiée avec succès.")
            except Exception as exc:
                QMessageBox.warning(self, "Erreur", str(exc))

    # Supprime l'entrée sélectionnée après confirmation.
    def delete_selected_entry(self) -> None:
        entry = self._selected_entry()
        if not entry:
            QMessageBox.information(self, "Information", "Veuillez sélectionner une entrée.")
            return
        answer = QMessageBox.question(
            self,
            "Confirmation",
            f"Supprimer l'entrée pour {entry.service_name} ?",
        )
        if answer == QMessageBox.Yes:
            try:
                self.vault_service.delete_entry(entry.id)
                self.refresh_entries()
                QMessageBox.information(self, "Succès", "Entrée supprimée.")
            except Exception as exc:
                QMessageBox.warning(self, "Erreur", str(exc))

    # Copie l'identifiant de l'entrée sélectionnée.
    def copy_selected_username(self) -> None:
        entry = self._selected_entry()
        if not entry:
            QMessageBox.information(self, "Information", "Veuillez sélectionner une entrée.")
            return
        QGuiApplication.clipboard().setText(entry.username)
        QMessageBox.information(self, "Copié", "Identifiant copié dans le presse papiers.")

    # Copie le mot de passe de l'entrée sélectionnée.
    def copy_selected_password(self) -> None:
        entry = self._selected_entry()
        if not entry:
            QMessageBox.information(self, "Information", "Veuillez sélectionner une entrée.")
            return
        QGuiApplication.clipboard().setText(entry.password)
        QMessageBox.information(self, "Copié", "Mot de passe copié dans le presse papiers.")

    # Écrit le fichier d'export JSON choisi par l'utilisateur.
    def export_entries(self) -> None:
        try:
            export_path_str, _ = QFileDialog.getSaveFileName(
                self,
                "Exporter le coffre",
                str(Path.home() / "safepass_export"),
                "SafePass (*.spass)",
            )
            if not export_path_str:
                return
            export_path = self.vault_service.export_entries(Path(export_path_str))
            QMessageBox.information(self, "Export réussi", f"Export enregistré dans\n{export_path}")
        except Exception as exc:
            QMessageBox.warning(self, "Erreur", str(exc))

    # Importe des entrées depuis un fichier exporté précédemment.
    def import_entries(self) -> None:
        try:
            import_path_str, _ = QFileDialog.getOpenFileName(
                self,
                "Importer un coffre",
                str(Path.home()),
                "SafePass (*.spass)",
            )
            if not import_path_str:
                return
            count = self.vault_service.import_entries(Path(import_path_str), overwrite_duplicates=True)
            self.refresh_entries()
            QMessageBox.information(self, "Import réussi", f"{count} entrée(s) importée(s).")
        except Exception as exc:
            QMessageBox.warning(self, "Erreur", str(exc))

    # Remplit le panneau de droite avec les valeurs de l'entrée sélectionnée.
    def update_details_panel(self) -> None:
        entry = self._selected_entry()
        if not entry:
            self.clear_details_panel()
            return
        self.detail_service[1].setText(entry.service_name or "-")
        self.detail_username[1].setText(entry.username or "-")
        self.detail_password[1].setText(entry.password or "-")
        self.detail_category[1].setText(entry.category or "-")
        self.detail_website[1].setText(entry.website or "-")
        self.detail_updated[1].setText(entry.updated_at or "-")
        self.notes_view.setPlainText(entry.notes or "")

    # Vide le panneau de détail lorsqu'aucune ligne n'est sélectionnée.
    def clear_details_panel(self) -> None:
        for _, label in [
            self.detail_service,
            self.detail_username,
            self.detail_password,
            self.detail_category,
            self.detail_website,
            self.detail_updated,
        ]:
            label.setText("-")
        self.notes_view.clear()

    # Déconnecte l'utilisateur puis revient à l'écran de connexion.
    def logout(self) -> None:
        self.vault_service.logout()
        self.close()
        self.on_logout()

    # Cette méthode est déclenchée par le minuteur d'inactivité.
    def logout_due_to_idle(self) -> None:
        QMessageBox.information(self, "Session verrouillée", "La session a été verrouillée après une période d'inactivité.")
        self.logout()
