from pathlib import Path
import unittest

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

    def test_revision_only_changed(self):
        self.assertTrue(self._manifest.equals_ignoring_revisions(self._rev_changed))

    def test_more_than_revision_changed(self):
        self.assertFalse(self._manifest.equals_ignoring_revisions(self._more_changed))

if __name__ == "__main__":
    unittest.main()