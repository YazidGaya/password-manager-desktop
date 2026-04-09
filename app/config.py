# Configuration générale de l'application SafePass.
from pathlib import Path

# Ce fichier contient les constantes principales de l'application.
APP_NAME = "SafePass"
APP_DIR = Path.home() / ".safepass"
APP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = APP_DIR / "vault.db"
EXPORT_EXT = ".spass"
PBKDF2_ITERATIONS = 390_000
BCRYPT_ROUNDS = 12
SESSION_IDLE_MINUTES = 10
