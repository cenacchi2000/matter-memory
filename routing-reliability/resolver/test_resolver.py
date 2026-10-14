import unittest, numpy as np
from resolver import Resolver
class Tests(unittest.TestCase):
 def setUp(self):
  rng=np.random.default_rng(4);self.frame=np.zeros((120,160,3),np.uint8);self.frame[35:55,45:65]=rng.integers(30,255,(20,20,3),dtype=np.uint8)
 def test_memory_is_immutable_during_loss(self):
  m=Resolver(self.frame,[45,35,20,20],30);before=m.anchor.copy();last=m.last.copy()
  for _ in range(12):r=m.step(np.zeros_like(self.frame))
  np.testing.assert_array_equal(m.anchor,before);np.testing.assert_array_equal(m.last,last);self.assertFalse(r['accepted']);self.assertAlmostEqual(r['evidence_age_s'],.4)
 def test_confirmation_needs_two_frames(self):
  m=Resolver(self.frame,[45,35,20,20],30);self.assertFalse(m.step(self.frame)['accepted']);self.assertTrue(m.step(self.frame)['accepted'])
 def test_prefix_determinism_and_no_future_access(self):
  a=Resolver(self.frame,[45,35,20,20],30);b=Resolver(self.frame,[45,35,20,20],30)
  for f in [self.frame,self.frame,np.zeros_like(self.frame)]:self.assertEqual(a.step(f),b.step(f))
 def test_hypotheses_finite_and_separate(self):
  m=Resolver(self.frame,[45,35,20,20]);r=m.step(np.zeros_like(self.frame));self.assertEqual(len(r['hypotheses']),3);self.assertTrue(np.isfinite(list(r['hypotheses'].values())).all());self.assertEqual(r['suggested_action'],'request_view_change')
if __name__=='__main__':unittest.main()
