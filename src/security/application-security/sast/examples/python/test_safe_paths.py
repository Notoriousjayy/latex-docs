import tempfile
import unittest
from pathlib import Path
from safe_paths import safe_path

class SafePathsTests(unittest.TestCase):
    def test_regular(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(safe_path(Path(d), "a.txt"), Path(d)/"a.txt")
    def test_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                safe_path(Path(d), "../outside")
    def test_absolute(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                safe_path(Path(d), "/etc/passwd")
    def test_missing(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                safe_path(Path(d), "")

if __name__ == '__main__':
    unittest.main()
