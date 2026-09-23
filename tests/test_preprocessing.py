import unittest

from app.services.preprocessing import (
    contains_citation,
    is_quotation,
    normalize_text,
    prepare_academic_text,
    split_passages,
    tokenize,
)


class PreprocessingTests(unittest.TestCase):
    def test_normalizes_spacing_and_quotes(self):
        self.assertEqual(normalize_text("  A   student\u2019s  work. "), "A student's work.")

    def test_tokenizes_case_insensitively(self):
        self.assertEqual(tokenize("Text-Similarity, TEXT!"), ["text", "similarity", "text"])

    def test_ignores_tiny_passages(self):
        passages = split_passages("Too short. This sentence contains enough useful words for comparison.")
        self.assertEqual(len(passages), 1)
        self.assertIn("enough useful words", passages[0].text)

    def test_removes_bibliography_section(self):
        text = (
            "This main discussion contains enough useful words for analysis.\n"
            "References\n"
            "Smith, J. (2024). A source that should not become a passage."
        )
        passages = split_passages(text)
        self.assertEqual(len(passages), 1)
        self.assertNotIn("Smith", passages[0].text)

    def test_removes_simple_document_boilerplate(self):
        text = "Page 1 of 3\nThis sentence contains the real academic discussion for comparison."
        self.assertNotIn("Page 1", prepare_academic_text(text))

    def test_identifies_common_citation_forms(self):
        self.assertTrue(contains_citation("The result was replicated (Smith, 2024)."))
        self.assertTrue(contains_citation("Smith (2024) reported the result."))
        self.assertTrue(contains_citation("The result was replicated [3]."))

    def test_identifies_predominantly_quoted_passage(self):
        text = '"Academic integrity requires proper acknowledgement of every source used in written work" (Smith, 2024).'
        self.assertTrue(is_quotation(text))
        passage = split_passages(text)[0]
        self.assertTrue(passage.is_quotation)
        self.assertTrue(passage.has_citation)


if __name__ == "__main__":
    unittest.main()
