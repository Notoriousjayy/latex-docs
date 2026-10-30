import unittest
from analyze_runs import percentile, summarize
from pathlib import Path
class MetricsTests(unittest.TestCase):
    def test_p95(self): self.assertAlmostEqual(percentile([1, 3, 5, 7, 9], 95), 8.6)
    def test_cohort(self):
        result = summarize(Path(__file__).with_name("sample-runs.csv"))
        self.assertEqual(result["baseline/warm"]["successful_samples"], 3)
if __name__ == "__main__": unittest.main()
