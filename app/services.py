# Couche de services qui centralise la logique métier de SafePass.
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from cryptography.fernet import Fernet

from .config import EXPORT_EXT
from .crypto_utils import (
    build_fernet,
    decrypt_text,
    encrypt_text,
    generate_password,
    generate_salt,
    hash_master_password,
    verify_master_password,
)
from .database import DatabaseManager


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class Entry:
    id: int
    service_name: str
    username: str
    password: str
    notes: str
    category: str
    website: str
    created_at: str
    updated_at: str


class VaultService:
    def __init__(self, db: Optional[DatabaseManager] = None) -> None:
        # Ce service centralise les règles métier de toute l'application.
        self.db = db or DatabaseManager()
        self.db.initialize()
        self._fernet: Optional[Fernet] = None
        self._user_email: Optional[str] = None

    # Indique à l'interface si un coffre existe déjà.
    def is_initialized(self) -> bool:
        return self.db.is_initialized()

    # Vérifie la robustesse du mot de passe maître.
    def validate_master_password_strength(self, password: str) -> None:
        if len(password) < 12:
            raise ValueError("Le mot de passe maître doit contenir au moins 12 caractères.")
        if not re.search(r"[a-z]", password):
            raise ValueError("Le mot de passe maître doit contenir une minuscule.")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Le mot de passe maître doit contenir une majuscule.")
        if not re.search(r"\d", password):
            raise ValueError("Le mot de passe maître doit contenir un chiffre.")
        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValueError("Le mot de passe maître doit contenir un caractère spécial.")

    # Crée le premier utilisateur local et enregistre le hash du mot de passe maître.
    def setup_vault(self, email: str, master_password: str, confirm_password: str) -> None:
        if self.is_initialized():
            raise ValueError("Le coffre est déjà initialisé.")
        if not email.strip():
            raise ValueError("L'email est obligatoire.")
        if not EMAIL_RE.match(email.strip()):
            raise ValueError("Format d'email invalide.")
        if master_password != confirm_password:
            raise ValueError("Les mots de passe ne correspondent pas.")
        self.validate_master_password_strength(master_password)

        encryption_salt = generate_salt()
        password_hash = hash_master_password(master_password)
        self.db.create_user(email.strip(), password_hash, encryption_salt)

    # Ouvre une session et prépare la clé Fernet en mémoire.
    def login(self, master_password: str) -> str:
        user = self.db.get_user()
        if not user:
            raise ValueError("Aucun coffre n'est initialisé.")
        if not verify_master_password(master_password, user["password_hash"]):
            raise ValueError("Mot de passe maître incorrect.")

        self._fernet = build_fernet(master_password, user["encryption_salt"])
        self._user_email = str(user["email"])
        return self._user_email

    # Ferme la session authentifiée en cours.
    def logout(self) -> None:
        self._fernet = None
        self._user_email = None

    @property
    def is_authenticated(self) -> bool:
        return self._fernet is not None

    # Protège les opérations sensibles derrière une session active.
    def _require_session(self) -> Fernet:
        if self._fernet is None:
            raise ValueError("Session non authentifiée.")
        return self._fernet

    # Chiffre puis enregistre une nouvelle entrée du coffre.
    def create_entry(self, service_name: str, username: str, password: str, notes: str = "", category: str = "", website: str = "") -> int:
        if not service_name.strip() or not username.strip() or not password.strip():
            raise ValueError("Le service, l'identifiant et le mot de passe sont obligatoires.")
        fernet = self._require_session()
        return self.db.add_entry(
            encrypt_text(fernet, service_name.strip()),
            encrypt_text(fernet, username.strip()),
            encrypt_text(fernet, password),
            encrypt_text(fernet, notes),
            encrypt_text(fernet, category),
            encrypt_text(fernet, website),
        )

    # Met à jour une entrée chiffrée existante.
    def update_entry(self, entry_id: int, service_name: str, username: str, password: str, notes: str = "", category: str = "", website: str = "") -> None:
        if not service_name.strip() or not username.strip() or not password.strip():
            raise ValueError("Le service, l'identifiant et le mot de passe sont obligatoires.")
        fernet = self._require_session()
        self.db.update_entry(
            entry_id,
            encrypt_text(fernet, service_name.strip()),
            encrypt_text(fernet, username.strip()),
            encrypt_text(fernet, password),
            encrypt_text(fernet, notes),
            encrypt_text(fernet, category),
            encrypt_text(fernet, website),
        )

    # Supprime une entrée à partir de son identifiant.
    def delete_entry(self, entry_id: int) -> None:
        self._require_session()
        self.db.delete_entry(entry_id)

    # Lit toutes les lignes depuis SQLite puis les déchiffre pour l'interface.
    def list_entries(self) -> List[Entry]:
        fernet = self._require_session()
        rows = self.db.fetch_entries()
        items: List[Entry] = []
        for row in rows:
            items.append(
                Entry(
                    id=int(row["id"]),
                    service_name=decrypt_text(fernet, row["service_name"]),
                    username=decrypt_text(fernet, row["username"]),
                    password=decrypt_text(fernet, row["password"]),
                    notes=decrypt_text(fernet, row["notes"]),
                    category=decrypt_text(fernet, row["category"]),
                    website=decrypt_text(fernet, row["website"]),
                    created_at=str(row["created_at"]),
                    updated_at=str(row["updated_at"]),
                )
            )
        return items

    # Retourne une entrée déchiffrée pour les opérations de modification.
    def get_entry(self, entry_id: int) -> Entry:
        fernet = self._require_session()
        row = self.db.fetch_entry_by_id(entry_id)
        if not row:
            raise ValueError("Entrée introuvable.")
        return Entry(
            id=int(row["id"]),
            service_name=decrypt_text(fernet, row["service_name"]),
            username=decrypt_text(fernet, row["username"]),
            password=decrypt_text(fernet, row["password"]),
            notes=decrypt_text(fernet, row["notes"]),
            category=decrypt_text(fernet, row["category"]),
            website=decrypt_text(fernet, row["website"]),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )

    # Expose le générateur de mots de passe intégré.
    def generate_suggested_password(self, length: int = 20, use_symbols: bool = True) -> str:
        return generate_password(length=length, use_symbols=use_symbols)

    # Exporte les entrées dans un fichier local au format JSON.
    def export_entries(self, export_path: Path) -> Path:
        entries = [entry.__dict__ for entry in self.list_entries()]
        export_path = export_path.with_suffix(EXPORT_EXT)
        export_path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
        return export_path

    # Importe des entrées et peut remplacer les doublons si nécessaire.
    def import_entries(self, import_path: Path, overwrite_duplicates: bool = False) -> int:
        self._require_session()
        existing = {(entry.service_name.lower(), entry.username.lower()): entry for entry in self.list_entries()}
        payload = json.loads(import_path.read_text(encoding="utf-8"))
        count = 0
        for item in payload:
            key = (item["service_name"].lower(), item["username"].lower())
            if key in existing and not overwrite_duplicates:
                continue
            if key in existing and overwrite_duplicates:
                self.update_entry(
                    existing[key].id,
                    item["service_name"],
                    item["username"],
                    item["password"],
                    item.get("notes", ""),
                    item.get("category", ""),
                    item.get("website", ""),
                )
            else:
                self.create_entry(
                    item["service_name"],
                    item["username"],
                    item["password"],
                    item.get("notes", ""),
                    item.get("category", ""),
                    item.get("website", ""),
                )
            count += 1
        return count
