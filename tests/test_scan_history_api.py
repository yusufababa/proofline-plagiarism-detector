import tempfile
import unittest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import router
from app.core.config import Settings
from app.domain import ScanResult
from app.repositories import ScanRepository


def result_for(name: str) -> ScanResult:
    return ScanResult(
        submitted_document=name,
        model_mode="lexical baseline",
        total_passages=1,
        matched_passages=0,
        reviewable_passages=1,
        excluded_passages=0,
        overall_score=0.0,
    )


class ScanHistoryApiTests(unittest.TestCase):
    def make_client(self, database_path: Path) -> tuple[TestClient, ScanRepository]:
        scans = ScanRepository(database_path)
        scans.initialize()
        application = FastAPI()
        application.include_router(router)
        application.state.settings = object()
        application.state.corpus = object()
        application.state.scans = scans
        application.state.scanner = object()
        return TestClient(application), scans

    def test_delete_endpoint_removes_one_record(self):
        with tempfile.TemporaryDirectory() as directory:
            client, scans = self.make_client(Path(directory) / "history.db")
            keep = scans.save(result_for("keep.txt"))
            remove = scans.save(result_for("remove.txt"))

            response = client.delete(f"/api/scans/{remove.id}")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["scan_id"], remove.id)
            self.assertIsNone(scans.get_result(remove.id))
            self.assertIsNotNone(scans.get_result(keep.id))

    def test_clear_endpoint_removes_every_record(self):
        with tempfile.TemporaryDirectory() as directory:
            client, scans = self.make_client(Path(directory) / "history.db")
            scans.save(result_for("one.txt"))
            scans.save(result_for("two.txt"))

            response = client.delete("/api/scans")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["deleted"], 2)
            self.assertEqual(scans.list_recent(), [])

    def test_scan_uses_system_temp_instead_of_project_upload_directory(self):
        class ScannerStub:
            def scan_text(self, filename: str, text: str) -> ScanResult:
                self.filename = filename
                self.text = text
                return result_for(filename)

        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory) / "project"
            settings = Settings(project_root=project_root)
            scans = ScanRepository(Path(directory) / "history.db")
            scans.initialize()
            scanner = ScannerStub()
            application = FastAPI()
            application.include_router(router)
            application.state.settings = settings
            application.state.corpus = object()
            application.state.scans = scans
            application.state.scanner = scanner
            client = TestClient(application)

            response = client.post(
                "/api/scan",
                files={
                    "file": (
                        "submission.txt",
                        b"Academic integrity requires clear acknowledgement of every source.",
                        "text/plain",
                    )
                },
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["submitted_document"], "submission.txt")
            self.assertEqual(scanner.filename, "submission.txt")
            self.assertIn("Academic integrity", scanner.text)
            self.assertFalse(settings.upload_dir.exists())


if __name__ == "__main__":
    unittest.main()
