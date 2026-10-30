import csv
from fractions import Fraction
from pathlib import Path
import tempfile
import unittest
from animation_time import FrameRate, Exposure, ExposureSheet, Cue, on_twos, smoothstep, contact_drift
from animation_fsm import Clip,AnimationController
from motion_physics import Body,Spring,FixedStepAccumulator

class FrameTests(unittest.TestCase):
    def test_conversion(self):
        self.assertEqual(FrameRate(24,1).frame_count(Fraction(5,2)),60)
        self.assertEqual(FrameRate(30000,1001).time_at(30000),Fraction(1001,1))
    def test_invalid_rate(self):
        with self.assertRaises(ValueError): FrameRate(0,1)
    def test_twos(self):
        self.assertEqual([e.length for e in on_twos(5).exposures],[2,2,1])
    def test_sheet_partition(self):
        with self.assertRaises(ValueError):
            ExposureSheet(4,[Exposure('a',0,2),Exposure('b',3,1)],[]).validate()
    def test_cue_bounds(self):
        with self.assertRaises(ValueError):
            ExposureSheet(2,[Exposure('a',0,2)],[Cue('late',1,3)]).validate()
    def test_rows(self):
        r=list(on_twos(6).rows(FrameRate()))
        self.assertEqual(len(r),6)
        self.assertEqual(r[0]['drawing'],r[1]['drawing'])
    def test_export(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'a.csv'
            on_twos(5).write_csv(str(out),FrameRate())
            with out.open(encoding='utf-8') as fin:
                self.assertEqual(len(list(csv.DictReader(fin))),5)
    def test_easing(self):
        self.assertEqual(smoothstep(0),0)
        self.assertEqual(smoothstep(1),1)
        self.assertAlmostEqual(smoothstep(.5),.5)
    def test_contact(self):
        self.assertAlmostEqual(contact_drift([(0,0),(3,4)]),5)
    def test_fsm(self):
        c=AnimationController({'idle':Clip('idle',1,True),'attack':Clip('attack',.5,False)})
        self.assertTrue(c.request('attack',{'idle'}))
        self.assertFalse(c.request('idle',{'idle'}))
        self.assertEqual(c.tick(3.0),1.0)
    def test_spring(self):
        s=Spring(1,0,0)
        for _ in range(120): s.step(1/120)
        self.assertLess(abs(s.position),.1)
    def test_fixed_step(self):
        times=[]
        a=FixedStepAccumulator(.01)
        n,alpha=a.advance(.025,times.append)
        self.assertEqual(n,2)
        self.assertAlmostEqual(sum(times),.02)
        self.assertAlmostEqual(alpha,.5)
    def test_mass(self):
        body=Body(0,0,2)
        body.advance(.1,10)
        self.assertAlmostEqual(body.velocity,.5)
if __name__=='__main__': unittest.main()
