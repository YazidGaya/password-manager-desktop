# SafePass - Gestionnaire de mots de passe local sécurisé

Application desktop développée en **Python** avec **PyQt5**.

## Fonctionnalités

- initialisation d'un coffre local au premier lancement ;
- authentification par mot de passe maître ;
- hachage du mot de passe maître avec **bcrypt** ;
- dérivation de clé de chiffrement via **PBKDF2-HMAC-SHA256** ;
- chiffrement des champs sensibles avec **Fernet** ;
- stockage local dans **SQLite** ;
- ajout, modification, suppression et recherche d'entrées ;
- générateur de mots de passe robustes ;
- export/import du coffre ;
- verrouillage automatique après inactivité.

## Structure du projet

```text
password_manager_completed/
├── app/
│   ├── config.py
│   ├── crypto_utils.py
│   ├── database.py
│   ├── services.py
│   ├── main.py
│   └── ui/
│       ├── dialogs.py
│       ├── login_window.py
│       ├── main_window.py
│       ├── setup_window.py
│       └── styles.py
├── tests/
├── requirements.txt
└── run.py
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
python run.py
```

## Sécurité

- le mot de passe maître n'est jamais stocké en clair ;
- la clé de chiffrement n'est pas enregistrée dans un fichier séparé du type `maCle.key` ;
- chaque coffre utilise un **salt** de dérivation dédié ;
- les entrées du coffre sont chiffrées avant insertion en base.

## Remarques

Le fichier SQLite est créé automatiquement dans :

- **Linux/macOS** : `~/.safepass/vault.db`
- **Windows** : `%USERPROFILE%\\.safepass\\vault.db`

## Pistes d'évolution

- masquage/affichage temporaire des mots de passe ;
- historique des modifications ;
- indicateur de robustesse de mot de passe ;
- empaquetage avec PyInstaller ;
- authentification secondaire locale.
