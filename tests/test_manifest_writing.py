#!/usr/bin/env python3

from pathlib import Path
import shutil
import tempfile
import unittest

from sc_manifest_parser import ScManifest

class TestManifestWriting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp_dir = tempfile.TemporaryDirectory()
        cls.tmp_path = Path(cls._tmp_dir.name)
        tests_dir = Path(__file__).parent.resolve()
        cls.fixture_dir = tests_dir / 'resources' / 'write_resources'

        cls.test_manifest = cls.tmp_path / 'manifest.xml'
    
    @classmethod
    def tearDownClass(cls):
        cls._tmp_dir.cleanup()
    
    def setUp(self):
        for item in self.tmp_path.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

        for file in self.fixture_dir.iterdir():
            shutil.copy(file, self.tmp_path)
    
    def test_update_attribute(self):
        manifest = ScManifest(self.test_manifest)

        for i in manifest.projects:
            i.name = "donut"
        manifest.write()

        manifest = ScManifest(self.test_manifest)
        for i in manifest.projects:
            self.assertEqual(i.name, "donut")
    
    def test_add_attribute(self):
        manifest = ScManifest(self.test_manifest)

        for i in manifest.projects:
            i.donut = "donut"
        manifest.write()
        
        manifest = ScManifest(self.test_manifest)
        for i in manifest.projects:
            self.assertEqual(i.donut, "donut")
    
    def test_del_att(self):
        manifest = ScManifest(self.test_manifest)

        for i in manifest.projects:
            del i.name
        manifest.write()

        manifest = ScManifest(self.test_manifest)
        for i in manifest.projects:
            self.assertEqual(i.name, None)

    def test_add_annotation(self):
        manifest = ScManifest(self.test_manifest)

        for i in manifest.projects:
            i.add_child("annotation", {"name": "donut", "value": "donut"})
        manifest.write()

        manifest = ScManifest(self.test_manifest)
        for i in manifest.projects:
            self.assertTrue(any(c.name == "donut" and c.value == "donut" for c in i.children))
        
    def test_remove(self):
        manifest = ScManifest(self.test_manifest)

        for i in manifest.projects:
            i.remove()
        manifest.write()
        
        manifest = ScManifest(self.test_manifest)
        self.assertEqual(manifest.projects, [])
            
if __name__ == "__main__":
    unittest.main()