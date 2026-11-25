import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate import validate
class Validation(unittest.TestCase):
    def setUp(self): self.data=json.loads((ROOT/'examples/example-manifest.json').read_text())
    def test_valid(self): self.assertEqual(validate(self.data),[])
    def test_dangling(self): self.data['relations'][0]['target']='E-MISSING'; self.assertTrue(validate(self.data))
    def test_observed_no_evidence(self): self.data['elements'][0]['status']='observed'; self.assertTrue(validate(self.data))
    def test_duplicate(self): self.data['elements'].append(copy.deepcopy(self.data['elements'][0])); self.assertTrue(validate(self.data))
    def test_uncovered(self): self.data['concerns'][0]['views']=[]; self.assertTrue(validate(self.data))
    def test_bad_baseline(self): self.data['baseline']=''; self.assertTrue(validate(self.data))
if __name__=='__main__': unittest.main()
