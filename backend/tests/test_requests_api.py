import os
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
                "request_date": "2026-10-08",
            },
        )
        self.assertEqual(created.status_code, 201)
        request_id = created.get_json()["id"]
        self.assertEqual(created.get_json()["status"], "pendiente")

        listed = self.client.get("/api/requests")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.get_json()), 1)

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


if __name__ == "__main__":
    unittest.main()