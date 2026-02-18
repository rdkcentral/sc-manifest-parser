from pathlib import Path
import unittest

from lxml import etree

from sc_manifest_parser import ScManifest


def make_tree(xml: str) -> etree._ElementTree:
    return etree.ElementTree(etree.fromstring(xml))


def make_manifest(xml_map: dict[str, str]) -> ScManifest:
    m = ScManifest.__new__(ScManifest)  # bypass __init__
    m.manifests = {
        Path(name): make_tree(xml)
        for name, xml in xml_map.items()
    }
    return m


class TestScManifestNormalized(unittest.TestCase):

    def test_identical_manifests_equal(self):
        xml = "<manifest><project name='a' revision='1'/></manifest>"

        m1 = make_manifest({"a.xml": xml})
        m2 = make_manifest({"a.xml": xml})

        self.assertEqual(m1.normalized(), m2.normalized())

    def test_ignore_revision_attribute(self):
        xml1 = "<manifest><project name='a' revision='1'/></manifest>"
        xml2 = "<manifest><project name='a' revision='2'/></manifest>"

        m1 = make_manifest({"a.xml": xml1})
        m2 = make_manifest({"a.xml": xml2})

        self.assertEqual(
            m1.normalized(ignore_attrs={"revision"}),
            m2.normalized(ignore_attrs={"revision"})
        )

    def test_revision_difference_detected_without_ignore(self):
        xml1 = "<manifest><project name='a' revision='1'/></manifest>"
        xml2 = "<manifest><project name='a' revision='2'/></manifest>"

        m1 = make_manifest({"a.xml": xml1})
        m2 = make_manifest({"a.xml": xml2})

        self.assertNotEqual(m1.normalized(), m2.normalized())

    def test_structure_difference_detected(self):
        xml1 = "<manifest><project name='a'/></manifest>"
        xml2 = "<manifest><project name='b'/></manifest>"

        m1 = make_manifest({"a.xml": xml1})
        m2 = make_manifest({"a.xml": xml2})

        self.assertNotEqual(m1.normalized(), m2.normalized())

    def test_missing_attribute_safe(self):
        xml = "<manifest><project name='a'/></manifest>"

        m = make_manifest({"a.xml": xml})

        # Should not raise
        try:
            m.normalized(ignore_attrs={"revision"})
        except Exception as e:
            self.fail(f"normalized() raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()