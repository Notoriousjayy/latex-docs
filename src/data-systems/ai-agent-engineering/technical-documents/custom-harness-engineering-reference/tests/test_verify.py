import unittest
from harness.verify import bounded_remediation, latex_diagnostics, run_gate
from pathlib import Path
from tempfile import TemporaryDirectory

class VerifyTests(unittest.TestCase):
    def test_diagnostics(self):
        self.assertEqual(len(latex_diagnostics('LaTeX Warning: x\nOverfull \\hbox x\nUnderfull \\vbox x')), 3)
        self.assertFalse(latex_diagnostics('Output written on guide.pdf'))
    def test_repair(self):
        results = iter([('FAIL','a'), ('PASS','')])
        self.assertEqual(bounded_remediation(lambda: next(results), lambda: True), 'PASS')
    def test_repeat(self):
        self.assertEqual(bounded_remediation(lambda: ('FAIL','a'), lambda: True), 'ESCALATE')
    def test_budget(self):
        results = iter([('FAIL','a'),('FAIL','b')])
        self.assertEqual(bounded_remediation(lambda: next(results), lambda: True,1), 'ESCALATE')
    def test_blocked(self):
        self.assertEqual(bounded_remediation(lambda: ('BLOCKED','x'),lambda: self.fail()),'ESCALATE')
    def test_gate_failure(self):
        with TemporaryDirectory() as d:
            p=Path(d); (p/'tests').mkdir(); (p/'tests/test_bad.py').write_text('import unittest\nclass T(unittest.TestCase):\n def test_bad(self): self.fail()\n')
            self.assertEqual(run_gate('unit',p).status,'FAIL')
    def test_gate_success(self):
        with TemporaryDirectory() as d:
            p=Path(d); (p/'tests').mkdir(); (p/'tests/test_ok.py').write_text('import unittest\nclass T(unittest.TestCase):\n def test_ok(self): pass\n')
            self.assertEqual(run_gate('unit',p).status,'PASS')
    def test_empty_gate(self):
        with TemporaryDirectory() as d:
            p=Path(d); (p/'tests').mkdir()
            self.assertEqual(run_gate('unit',p).status,'FAIL')
    def test_unknown_gate(self):
        with self.assertRaises(ValueError): run_gate('unsafe',Path.cwd())
