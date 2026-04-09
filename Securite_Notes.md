# Notes de sécurité

## Problèmes observés dans la version initiale

- une clé Fernet était stockée dans `maCle.key` ;
- des identifiants étaient conservés en clair dans `mesInfo.txt` ;
- le chiffrement était testé via un script monolithique sans séparation claire des responsabilités.

## Corrections apportées

- suppression du principe de clé statique dans le dépôt ;
- dérivation de clé depuis le mot de passe maître et un salt dédié ;
- stockage chiffré des champs sensibles dans SQLite ;
- mot de passe maître uniquement haché ;
- architecture modulaire facilitant les audits et les évolutions.
