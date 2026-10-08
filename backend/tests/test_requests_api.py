import os
import sqlite3
import tempfile
import unittest

from app import create_app


class RequestsApiTest(unittest.TestCase):
    def setUp(self):
        self.database_file = tempfile.NamedTemporaryFile(delete=False)
        self.database_file.close()
        self.app = create_app({"TESTING": True, "DATABASE": self.database_file.name})
        self.client = self.app.test_client()

    def tearDown(self):
        os.unlink(self.database_file.name)

    def test_create_list_and_update_status(self):
        created = self.client.post(
            "/api/requests",
            json={
                "applicant_name": "Ana Pérez",
                "document_type": "Cédula",
                "document_number": "123456789",
                "request_date": "2026-10-08",
            },
        )
        self.assertEqual(created.status_code, 201)
        request_id = created.get_json()["id"]
        self.assertEqual(created.get_json()["status"], "pendiente")
        self.assertEqual(created.get_json()["document_number"], "123456789")

        listed = self.client.get("/api/requests")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.get_json()), 1)
        self.assertEqual(listed.get_json()[0]["document_number"], "123456789")

        updated = self.client.patch(
            f"/api/requests/{request_id}/status", json={"status": "aprobada"}
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.get_json()["status"], "aprobada")

    def test_validation_and_missing_request_errors(self):
        empty_request = self.client.post("/api/requests", json={})
        self.assertEqual(empty_request.status_code, 400)

        missing_request = self.client.patch(
            "/api/requests/999/status", json={"status": "aprobada"}
        )
        self.assertEqual(missing_request.status_code, 404)

    def test_existing_database_is_migrated(self):
        legacy_database = tempfile.NamedTemporaryFile(delete=False)
        legacy_database.close()
        try:
            database = sqlite3.connect(legacy_database.name)
            try:
                database.execute(
                    "CREATE TABLE requests ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "applicant_name TEXT NOT NULL, document_type TEXT NOT NULL, "
                    "request_date TEXT NOT NULL, status TEXT NOT NULL "
                    "DEFAULT 'pendiente')"
                )
                database.execute(
                    "INSERT INTO requests (applicant_name, document_type, request_date) "
                    "VALUES ('Luis Díaz', 'DNI', '2026-10-08')"
                )
                database.commit()
            finally:
                database.close()

            migrated_app = create_app(
                {"TESTING": True, "DATABASE": legacy_database.name}
            )
            response = migrated_app.test_client().get("/api/requests")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()[0]["applicant_name"], "Luis Díaz")
            self.assertEqual(response.get_json()[0]["document_number"], "")
        finally:
            os.unlink(legacy_database.name)


if __name__ == "__main__":
    unittest.main()