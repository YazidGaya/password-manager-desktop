# Gestion de la base de données SQLite locale.
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional

from .config import DB_PATH


class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        # Vérifie que le dossier local de l'application existe.
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self):
        # Encadre les opérations SQL avec validation ou annulation en cas d'erreur.
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # Crée les tables nécessaires si elles n'existent pas encore.
    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password_hash BLOB NOT NULL,
                    encryption_salt BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS vault_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name BLOB NOT NULL,
                    username BLOB NOT NULL,
                    password BLOB NOT NULL,
                    notes BLOB,
                    category BLOB,
                    website BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    # Indique si un utilisateur existe déjà dans le coffre local.
    def is_initialized(self) -> bool:
        self.initialize()
        with self.connect() as conn:
            cursor = conn.execute("SELECT COUNT(*) AS count FROM users")
            return cursor.fetchone()["count"] > 0

    # Enregistre le premier utilisateur local.
    def create_user(self, email: str, password_hash: bytes, encryption_salt: bytes) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO users (email, password_hash, encryption_salt) VALUES (?, ?, ?)",
                (email, password_hash, encryption_salt),
            )

    # Récupère l'utilisateur local actuellement enregistré.
    def get_user(self) -> Optional[sqlite3.Row]:
        with self.connect() as conn:
            cursor = conn.execute(
                "SELECT id, email, password_hash, encryption_salt, created_at FROM users LIMIT 1"
            )
            return cursor.fetchone()

    # Ajoute une entrée chiffrée dans le coffre.
    def add_entry(
        self,
        service_name: bytes,
        username: bytes,
        password: bytes,
        notes: bytes,
        category: bytes,
        website: bytes,
    ) -> int:
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO vault_entries (service_name, username, password, notes, category, website)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (service_name, username, password, notes, category, website),
            )
            return int(cursor.lastrowid)

    # Met à jour une entrée chiffrée du coffre.
    def update_entry(
        self,
        entry_id: int,
        service_name: bytes,
        username: bytes,
        password: bytes,
        notes: bytes,
        category: bytes,
        website: bytes,
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE vault_entries
                SET service_name = ?, username = ?, password = ?, notes = ?, category = ?, website = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (service_name, username, password, notes, category, website, entry_id),
            )

    # Supprime une entrée à partir de son identifiant.
    def delete_entry(self, entry_id: int) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM vault_entries WHERE id = ?", (entry_id,))

    # Récupère toutes les entrées chiffrées triées par dernière modification.
    def fetch_entries(self) -> List[sqlite3.Row]:
        with self.connect() as conn:
            cursor = conn.execute(
                "SELECT id, service_name, username, password, notes, category, website, created_at, updated_at "
                "FROM vault_entries ORDER BY updated_at DESC, id DESC"
            )
            return cursor.fetchall()

    # Récupère une entrée à partir de son identifiant.
    def fetch_entry_by_id(self, entry_id: int) -> Optional[sqlite3.Row]:
        with self.connect() as conn:
            cursor = conn.execute(
                "SELECT id, service_name, username, password, notes, category, website, created_at, updated_at "
                "FROM vault_entries WHERE id = ?",
                (entry_id,),
            )
            return cursor.fetchone()
