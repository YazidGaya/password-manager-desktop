# Point d'entrée de l'interface graphique SafePass.
from __future__ import annotations

import sys

from PyQt5.QtWidgets import QApplication

from .services import VaultService
from .ui.login_window import LoginWindow
from .ui.main_window import MainWindow
from .ui.setup_window import SetupWindow
from .ui.styles import APP_STYLESHEET


class AppController:
    def __init__(self) -> None:
        # Crée l'application Qt et la couche de services partagée.
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("SafePass")
        self.app.setStyleSheet(APP_STYLESHEET)
        self.vault_service = VaultService()
        self.current_window = None

    # Choisit d'afficher d'abord la fenêtre d'initialisation ou de connexion.
    def show_startup(self) -> None:
        if self.vault_service.is_initialized():
            self.show_login()
        else:
            self.show_setup()

    # Ouvre la fenêtre d'initialisation au premier lancement.
    def show_setup(self) -> None:
        self.current_window = SetupWindow(self.vault_service, self.show_login)
        self.current_window.show()

    # Ouvre la fenêtre de connexion.
    def show_login(self) -> None:
        self.current_window = LoginWindow(self.vault_service, self.show_main)
        self.current_window.show()

    # Ouvre la fenêtre principale du coffre après une connexion réussie.
    def show_main(self, user_email: str) -> None:
        self.current_window = MainWindow(self.vault_service, user_email, self.show_login)
        self.current_window.show()

    # Lance la boucle principale de l'interface Qt.
    def run(self) -> int:
        self.show_startup()
        return self.app.exec_()


# Point d'entrée public du projet.
def main() -> int:
    controller = AppController()
    return controller.run()


if __name__ == "__main__":
    raise SystemExit(main())
