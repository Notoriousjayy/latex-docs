"""Verify AI Agent lab presentation coverage and reproducibility metadata."""
import csv
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"src/data-systems/ai-agent-engineering/curriculum/lab-presentations"
class LabPresentationTests(unittest.TestCase):
    def test_16_decks(self):
        decks=sorted(BASE.glob("l[0-9][0-9]-*.tex"))
        self.assertEqual(16,len(decks))
        for index,deck in enumerate(decks,1):
            txt=deck.read_text(encoding="utf-8")
            self.assertTrue(deck.name.startswith(f"l{index:02d}-"))
            self.assertIn(r"\\documentclass[aspectratio=169,10pt]{beamer}",txt)
            self.assertGreaterEqual(txt.count(r"\\begin{frame}"),25)
            for term in ("Architecture and data flow","Negative and adversarial verification","Acceptance criteria","Reproducibility and evidence"):
                self.assertIn(term,txt)
    def test_manifest(self):
        with (BASE/"lab-coverage-matrix.csv").open(newline="",encoding="utf-8") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(16,len(rows))
        for i,row in enumerate(rows,1):
            self.assertEqual(f"L{i:02d}",row["lab_id"])
            self.assertTrue((ROOT/row["presentation_path"]).is_file())
            self.assertTrue(row["source_commit_sha"])
if __name__=="__main__": unittest.main()
