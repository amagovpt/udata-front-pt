import unittest
from udata_front.security import sanitize_svg


class TestSVGSanitization(unittest.TestCase):

    def test_basic_script_removal(self):
        payload = b"<svg><script>alert(1)</script></svg>"
        cleaned = sanitize_svg(payload)
        self.assertNotIn(b"script", cleaned)
        self.assertNotIn(b"alert", cleaned)

    def test_onload_attribute_removal(self):
        payload = b'<svg onload="alert(1)"></svg>'
        cleaned = sanitize_svg(payload)
        self.assertNotIn(b"onload", cleaned)

    def test_malformed_svg_rejection(self):
        payload = b'<svg onload="alert(1)">'  # Missing closing tag
        with self.assertRaises(ValueError):
            sanitize_svg(payload)

    def test_javascript_href_removal(self):
        payload = b'<svg><a href="javascript:alert(1)">Click me</a></svg>'
        cleaned = sanitize_svg(payload)
        self.assertNotIn(b"javascript:", cleaned)
        self.assertIn(b"Click me", cleaned)

    def test_namespaced_script_removal(self):
        payload = (
            b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
        )
        cleaned = sanitize_svg(payload)
        self.assertNotIn(b"script", cleaned)

    def test_valid_svg_pass(self):
        payload = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" stroke="green" stroke-width="4" fill="yellow" /></svg>'
        cleaned = sanitize_svg(payload)
        self.assertIn(b"circle", cleaned)
        self.assertIn(b'fill="yellow"', cleaned)
        # Verify structure remains valid XML
        self.assertTrue(cleaned.startswith(b"<?xml"))

    def test_foreign_object_removal(self):
        payload = b"<svg><foreignObject><body><script>alert(1)</script></body></foreignObject></svg>"
        cleaned = sanitize_svg(payload)
        self.assertNotIn(b"foreignObject", cleaned)


if __name__ == "__main__":
    unittest.main()
