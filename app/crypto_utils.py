# Fonctions utilitaires liées au hachage, au chiffrement et aux mots de passe.
from __future__ import annotations

import base64
import secrets
import string
from typing import Optional

import bcrypt
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .config import PBKDF2_ITERATIONS, BCRYPT_ROUNDS


# Génère un sel aléatoire utilisé pour dériver la clé de chiffrement.
def generate_salt(length: int = 16) -> bytes:
    return secrets.token_bytes(length)


# Hache le mot de passe maître avec bcrypt.
def hash_master_password(master_password: str) -> bytes:
    password_bytes = master_password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(password_bytes, salt)


# Vérifie un mot de passe en clair avec le hash bcrypt stocké.
def verify_master_password(master_password: str, password_hash: bytes) -> bool:
    return bcrypt.checkpw(master_password.encode("utf-8"), password_hash)


# Dérive une clé compatible Fernet à partir du mot de passe maître.
def derive_fernet_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode("utf-8")))
    return key


# Crée l'objet Fernet utilisé pour le chiffrement et le déchiffrement.
def build_fernet(master_password: str, salt: bytes) -> Fernet:
    return Fernet(derive_fernet_key(master_password, salt))


# Chiffre un champ texte avant son enregistrement dans SQLite.
def encrypt_text(fernet: Fernet, plaintext: str) -> bytes:
    return fernet.encrypt(plaintext.encode("utf-8"))


# Déchiffre un champ relu depuis SQLite.
def decrypt_text(fernet: Fernet, ciphertext: Optional[bytes]) -> str:
    if not ciphertext:
        return ""
    try:
        return fernet.decrypt(ciphertext).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Impossible de déchiffrer la donnée : clé invalide ou donnée corrompue.") from exc


# Génère un mot de passe fort aléatoire pour l'utilisateur.
def generate_password(length: int = 20, use_symbols: bool = True) -> str:
    if length < 8:
        raise ValueError("La longueur minimale recommandée est de 8 caractères.")

    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+[]{};:,.?/"

    charset = lower + upper + digits + (symbols if use_symbols else "")
    mandatory = [
        secrets.choice(lower),
        secrets.choice(upper),
        secrets.choice(digits),
    ]
    if use_symbols:
        mandatory.append(secrets.choice(symbols))

    remaining = length - len(mandatory)
    password_chars = mandatory + [secrets.choice(charset) for _ in range(remaining)]
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)
