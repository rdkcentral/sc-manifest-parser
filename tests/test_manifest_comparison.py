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


class TestScManifestEquals(unittest.TestCase):

    def test_identical_manifests_equal(self):
        xml = "<manifest><project name='a' revision='1'/></manifest>"

        m1 = make_manifest({"a.xml": xml})
        m2 = make_manifest({"a.xml": xml})

        self.assertTrue(m1.equals(m2))

    def test_ignore_revision_attribute(self):
        xml1 = "<manifest><project name='a' revision='1'/></manifest>"
        xml2 = "<manifest><project name='a' revision='2'/></manifest>"

        m1 = make_manifest({"a.xml": xml1})
        m2 = make_manifest({"a.xml": xml2})

        self.assertTrue(m1.equals(m2, ignore_attrs={"revision"}))

    def test_revision_difference_detected_without_ignore(self):
        xml1 = "<manifest><project name='a' revision='1'/></manifest>"
        xml2 = "<manifest><project name='a' revision='2'/></manifest>"

        m1 = make_manifest({"a.xml": xml1})
        m2 = make_manifest({"a.xml": xml2})

        self.assertFalse(m1.equals(m2))

    def test_structure_difference_detected(self):
        xml1 = "<manifest><project name='a'/></manifest>"
        xml2 = "<manifest><project name='b'/></manifest>"

        m1 = make_manifest({"a.xml": xml1})
        m2 = make_manifest({"a.xml": xml2})

        self.assertFalse(m1.equals(m2))

if __name__ == "__main__":
    unittest.main()