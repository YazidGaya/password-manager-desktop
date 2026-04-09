# Tests de base pour vérifier le fonctionnement du service principal.
from pathlib import Path
import tempfile
import unittest

from app.database import DatabaseManager
from app.services import VaultService


class VaultServiceTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tempdir.name) / "test.db"
        self.service = VaultService(DatabaseManager(self.db_path))

    def tearDown(self):
        self.tempdir.cleanup()

    def test_setup_login_and_crud(self):
        self.service.setup_vault("user@example.com", "MasterPass!2026", "MasterPass!2026")
        self.assertTrue(self.service.is_initialized())
        email = self.service.login("MasterPass!2026")
        self.assertEqual(email, "user@example.com")

        entry_id = self.service.create_entry(
            "GitHub",
            "user@example.com",
            "Secret!123",
            notes="Compte principal",
            category="Développement",
            website="https://github.com",
        )
        self.assertGreater(entry_id, 0)
        entries = self.service.list_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].service_name, "GitHub")

        self.service.update_entry(
            entry_id,
            "GitHub",
            "user@example.com",
            "Updated!456",
            notes="Compte mis à jour",
            category="Dev",
            website="https://github.com",
        )
        entry = self.service.get_entry(entry_id)
        self.assertEqual(entry.password, "Updated!456")

        self.service.delete_entry(entry_id)
        self.assertEqual(len(self.service.list_entries()), 0)


if __name__ == "__main__":
    unittest.main()
