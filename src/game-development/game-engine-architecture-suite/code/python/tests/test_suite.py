"""Portable unittest tests for teaching reference implementations."""
import math
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fixed_loop import simulate
from animation_math import slerp, normalize
from rasterizer import render
from physics import Body,tick
from audio_mixer import synthesize
from ecs_events import World
from frame_metrics import quantile_nearest_rank,analyze

class EngineExercises(unittest.TestCase):
    def test_fixed_step_render_rate_independence(self):
        a=simulate([10_000]*100)
        b=simulate([20_000]*50)
        self.assertEqual(a[0].ticks,b[0].ticks)
        self.assertAlmostEqual(a[0].pos,b[0].pos)
    def test_overload_drops_ticks(self):
        state,dropped,alpha=simulate([250_000],max_ticks_per_frame=4)
        self.assertEqual(state.ticks,4)
        self.assertEqual(dropped,21)
        self.assertEqual(alpha,0)
    def test_slerp(self):
        q=slerp((1,0,0,0),(0,0,0,1),.5)
        self.assertAlmostEqual(sum(x*x for x in q),1)
        self.assertAlmostEqual(slerp((1,0,0,0),(-1,0,0,0),.5)[0],1)
    def test_rasterizer(self):
        pix=render()
        self.assertEqual(len(pix),96*96)
        self.assertIn((230,140,60),pix)
    def test_physics(self):
        body=Body()
        for _ in range(1000):tick(body,.01)
        self.assertGreaterEqual(body.y,0)
        self.assertTrue(math.isfinite(body.vy))
    def test_audio(self):
        samples,clipped=synthesize(.01)
        self.assertEqual(len(samples),480)
        self.assertEqual(clipped,0)
        self.assertLessEqual(max(map(abs,samples)),32767)
    def test_events_and_generation(self):
        w=World(); old=w.spawn('a');self.assertTrue(w.destroy(old));new=w.spawn('b')
        self.assertIsNone(w.get(old))
        self.assertEqual(w.get(new),'b')
        out=[];w.emit('first');w.emit('second');w.drain(out.append)
        self.assertEqual(out,['first','second'])
    def test_percentile(self):
        self.assertEqual(quantile_nearest_rank([1,2,3,4,5],.95),5)
        self.assertEqual(analyze([10.,20.])['over_budget'],1)

if __name__=='__main__':unittest.main()
