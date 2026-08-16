import unittest

from lxml import etree

from scripts.verify_epub_source import canonicalize


class SourceHtmlCanonicalizationTests(unittest.TestCase):
    def test_inherited_namespace_context_is_ignored(self):
        document = etree.fromstring(
            b'<html xmlns="http://www.w3.org/1999/xhtml"><table><tr><th><p><strong>Header</strong></p></th></tr></table></html>'
        )
        source_node = document.xpath(
            "//*[local-name()='th']"
        )[0]
        standalone = etree.fromstring(
            b'<th xmlns="http://www.w3.org/1999/xhtml"><p><strong>Header</strong></p></th>'
        )
        self.assertEqual(canonicalize(source_node), canonicalize(standalone))

    def test_real_content_change_is_detected(self):
        first = etree.fromstring(b"<th><p>Header</p></th>")
        second = etree.fromstring(b"<th><p>Changed</p></th>")
        self.assertNotEqual(canonicalize(first), canonicalize(second))


if __name__ == "__main__":
    unittest.main()
