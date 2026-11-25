import tempfile
import unittest
from pathlib import Path

from tooling.scripts.verify_diagram_pairs import verify


class DiagramPairTests(unittest.TestCase):
    def test_named_multiple_blocks_and_config(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "config.puml").write_text("skinparam backgroundColor white")
            (root / "d.puml").write_text("@startuml first\nA -> B\n@enduml\n@startuml second\nB -> A\n@enduml\n")
            for fmt in ("png", "svg"):
                (root / fmt).mkdir()
                for name in ("first", "second"):
                    (root / fmt / (name + "." + fmt)).write_bytes(b"\x89PNG\r\n\x1a\n" if fmt == "png" else b"<svg/>")
            self.assertEqual([], verify([root]))
            (root / "svg" / "second.svg").unlink()
            self.assertTrue(any("second.svg" in issue for issue in verify([root])))
            (root / "legacy.jpg").write_bytes(b"legacy")
            self.assertTrue(any("Legacy JPEG prohibited" in issue for issue in verify([root])))


if __name__ == "__main__":
    unittest.main()
