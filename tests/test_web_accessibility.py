import unittest
from html.parser import HTMLParser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ElementCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.elements.append((tag, dict(attrs)))


class WebAccessibilityTests(unittest.TestCase):
    def test_page_has_keyboard_skip_target_and_live_regions(self):
        parser = ElementCollector()
        parser.feed(
            (PROJECT_ROOT / "app" / "web" / "templates" / "index.html").read_text(
                encoding="utf-8"
            )
        )
        elements = parser.elements

        self.assertIn(
            ("a", {"class": "skip-link", "href": "#main-content"}),
            elements,
        )
        main = next(attrs for tag, attrs in elements if tag == "main")
        self.assertEqual(main["id"], "main-content")
        self.assertEqual(main["tabindex"], "-1")
        self.assertGreaterEqual(
            sum(attrs.get("aria-live") == "polite" for _, attrs in elements), 3
        )

    def test_styles_support_visible_focus_and_reduced_motion(self):
        styles = (PROJECT_ROOT / "app" / "web" / "static" / "styles.css").read_text(
            encoding="utf-8"
        )
        script = (PROJECT_ROOT / "app" / "web" / "static" / "app.js").read_text(
            encoding="utf-8"
        )

        self.assertIn(":focus-visible", styles)
        self.assertIn("prefers-reduced-motion", styles)
        self.assertIn("window.confirm", script)
        self.assertIn("aria-label=\"Delete saved scan", script)

    def test_redesigned_composer_and_dashboard_keep_core_workflows_accessible(self):
        parser = ElementCollector()
        parser.feed(
            (PROJECT_ROOT / "app" / "web" / "templates" / "index.html").read_text(
                encoding="utf-8"
            )
        )
        elements = parser.elements
        element_ids = {attrs.get("id") for _, attrs in elements if attrs.get("id")}
        navigation_panels = {
            attrs.get("data-panel") for tag, attrs in elements if tag == "button"
        }

        self.assertTrue(
            {
                "scan-text",
                "scan-file",
                "scan-submit",
                "dashboard-view",
                "results-section",
                "scan-history",
                "reference-dropzone",
            }.issubset(element_ids)
        )
        self.assertTrue(
            {"overview", "evidence", "history", "library", "project"}.issubset(
                navigation_panels
            )
        )

        script = (PROJECT_ROOT / "app" / "web" / "static" / "app.js").read_text(
            encoding="utf-8"
        )
        self.assertIn("new File([text]", script)
        self.assertIn("setupComposerDropzone", script)


if __name__ == "__main__":
    unittest.main()
