"""Standard-library tests for the example release utilities."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parent

def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class DeliveryTests(unittest.TestCase):
    def test_provenance_roundtrip_and_tamper(self):
        b = load("build_artifact")
        v = load("verify_artifact")
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "function.py"
            src.write_text("def handler(x,y): return 1\n")
            path = Path(tmp) / "function.zip"
            b.build(src, path, "abc123")
            manifest = path.with_suffix(".zip.manifest.json")
            self.assertTrue(v.verify(path, manifest, "abc123"))
            self.assertFalse(v.verify(path, manifest, "wrong-revision"))
            path.write_bytes(path.read_bytes() + b"tamper")
            self.assertFalse(v.verify(path, manifest, "abc123"))

    def test_canary_abort(self):
        c = load("canary_simulator")
        checks = c.assess([10,50,100], [{"requests":200,"errors":0}, {"requests":200,"errors":7}])
        self.assertEqual([r["decision"] for r in checks], ["PROMOTE", "ABORT"])

    def test_security_gate(self):
        g = load("gate_policy")
        self.assertFalse(g.gate([{"disposition":"block","rule":"secrets"}])[0])
        self.assertTrue(g.gate([])[0])

if __name__ == "__main__":
    unittest.main()
