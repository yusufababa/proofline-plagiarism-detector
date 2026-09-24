import tempfile
import unittest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.staticfiles import StaticFiles

from app.core.config import Settings
from app.core.security import BasicAccessMiddleware
from app.services.demo_data import seed_demo_references


class DeploymentTests(unittest.TestCase):
    def test_checked_in_stylesheet_is_served_as_css(self):
        project_root = Path(__file__).resolve().parents[1]
        application = FastAPI()
        application.mount(
            "/static",
            StaticFiles(directory=project_root / "app" / "web" / "static"),
            name="static",
        )

        response = TestClient(application).get("/static/styles.css")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("text/css"))
        self.assertIn("--canvas", response.text)

    def test_hosted_access_password_protects_application_but_not_health(self):
        application = FastAPI()

        @application.get("/")
        def home() -> dict:
            return {"status": "private"}

        @application.get("/api/health")
        def health() -> dict:
            return {"status": "ok"}

        application.add_middleware(
            BasicAccessMiddleware,
            username="proofline",
            password="safe-demo-password",
            excluded_paths=frozenset({"/api/health"}),
        )
        client = TestClient(application)

        self.assertEqual(client.get("/").status_code, 401)
        self.assertEqual(client.get("/api/health").status_code, 200)
        self.assertEqual(
            client.get("/", auth=("proofline", "safe-demo-password")).status_code,
            200,
        )

    def test_blank_password_keeps_localhost_mode_open(self):
        application = FastAPI()

        @application.get("/")
        def home() -> dict:
            return {"status": "open"}

        application.add_middleware(
            BasicAccessMiddleware,
            username="proofline",
            password="",
        )
        self.assertEqual(TestClient(application).get("/").status_code, 200)

    def test_demo_corpus_is_seeded_once(self):
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            corpus_dir = project_root / "lecturer_demo" / "Corpus"
            corpus_dir.mkdir(parents=True)
            (corpus_dir / "example.txt").write_text("Example reference", encoding="utf-8")
            (corpus_dir / "ignored.csv").write_text("Not supported", encoding="utf-8")
            config = Settings(project_root=project_root, seed_demo_corpus=True)

            self.assertEqual(seed_demo_references(config), 1)
            self.assertEqual(seed_demo_references(config), 0)
            self.assertEqual(
                (config.reference_dir / "example.txt").read_text(encoding="utf-8"),
                "Example reference",
            )


if __name__ == "__main__":
    unittest.main()
