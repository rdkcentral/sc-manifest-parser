from pathlib import Path
import unittest
import tempfile

from sc_manifest_parser import ScManifest

class ManifestComparisonTester(unittest.TestCase):
    def setUp(self) -> ScManifest:
    resource_dir = Path(__file__).resolve().parent / "resources"
    test_man_path = resource_dir / "test_manifest.xml"
    self._manifest = ScManifest(test_man_path)

    rev_change_path = resource_dir / "comparison_resources" / "revs_changed" / "test_manifest.xml"
    self._rev_changed = ScManifest(rev_change_path)

    more_change_path = resource_dir / "comparison_resources" / "more_changed" / "test_manifest.xml"
    self._more_changed = ScManifest(more_change_path)

    def _manifest_from_xml(self, xml: str) -> ScManifest:
    """
    Helper to create a ScManifest instance from an XML string by writing it
    to a temporary file and parsing it.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "manifest.xml"
        path.write_text(xml, encoding="utf-8")
        # ScManifest is expected to read and parse the manifest at construction time.
        return ScManifest(path)

    def test_revision_only_changed(self):
    self.assertTrue(self._manifest.equals_ignoring_revisions(self._rev_changed))

    def test_more_than_revision_changed(self):
    self.assertFalse(self._manifest.equals_ignoring_revisions(self._more_changed))

    def test_equals_no_projects(self):
    xml = "<manifest></manifest>"
    manifest_a = self._manifest_from_xml(xml)
    manifest_b = self._manifest_from_xml(xml)
    self.assertTrue(manifest_a.equals_ignoring_revisions(manifest_b))

    def test_different_number_of_projects(self):
    xml_many_projects = (
        "<manifest>"
        "<project name='a' path='a' revision='r1'/>"
        "<project name='b' path='b' revision='r2'/>"
        "</manifest>"
    )
    xml_fewer_projects = (
        "<manifest>"
        "<project name='a' path='a' revision='r1'/>"
        "</manifest>"
    )
    manifest_many = self._manifest_from_xml(xml_many_projects)
    manifest_few = self._manifest_from_xml(xml_fewer_projects)
    self.assertFalse(manifest_many.equals_ignoring_revisions(manifest_few))

    def test_missing_vs_present_revisions(self):
    xml_with_revs = (
        "<manifest>"
        "<project name='a' path='a' revision='r1'/>"
        "<project name='b' path='b' revision='r2'/>"
        "</manifest>"
    )
    xml_without_revs = (
        "<manifest>"
        "<project name='a' path='a'/>"
        "<project name='b' path='b'/>"
        "</manifest>"
    )
    manifest_with_revs = self._manifest_from_xml(xml_with_revs)
    manifest_without_revs = self._manifest_from_xml(xml_without_revs)
    self.assertTrue(manifest_with_revs.equals_ignoring_revisions(manifest_without_revs))

    def test_nested_includes_ignoring_revision_differences(self):
    """
    Ensure that manifests which use includes are considered equal when they
    differ only by project revisions in included files.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Included manifests with the same projects but different revisions.
        included1_path = tmp_path / "included1.xml"
        included2_path = tmp_path / "included2.xml"

        included1_xml = (
            "<manifest>"
            "<project name='a' path='a' revision='r1'/>"
            "</manifest>"
        )
        included2_xml = (
            "<manifest>"
            "<project name='a' path='a' revision='r2'/>"
            "</manifest>"
        )

        included1_path.write_text(included1_xml, encoding="utf-8")
        included2_path.write_text(included2_xml, encoding="utf-8")

        # Main manifests that include the respective included manifests.
        main1_path = tmp_path / "main1.xml"
        main2_path = tmp_path / "main2.xml"

        main1_xml = (
            "<manifest>"
            f"<include name='{included1_path.name}'/>"
            "</manifest>"
        )
        main2_xml = (
            "<manifest>"
            f"<include name='{included2_path.name}'/>"
            "</manifest>"
        )

        main1_path.write_text(main1_xml, encoding="utf-8")
        main2_path.write_text(main2_xml, encoding="utf-8")

        manifest_main1 = ScManifest(main1_path)
        manifest_main2 = ScManifest(main2_path)

        self.assertTrue(manifest_main1.equals_ignoring_revisions(manifest_main2))
if __name__ == "__main__":
    unittest.main()