import unittest
import pandas as pd
from picks import _market_anchored_probability, _push_probability, _expected_return


class PushTests(unittest.TestCase):
    def test_integer_line_accounts_for_all_outcomes(self):
        h=pd.Series([1.,2.,3.]); c=pd.Series(dtype=float)
        over,_=_market_anchored_probability(h,c,2,'OVER',.5)
        under,_=_market_anchored_probability(h,c,2,'UNDER',.5)
        push=_push_probability(h,c,2)
        self.assertEqual(over,.5)
        self.assertEqual(under,.5)
        self.assertAlmostEqual((over+under)*(1-push)+push,1)
        self.assertAlmostEqual(_expected_return(over,100,push),0)
        self.assertAlmostEqual(_expected_return(over,-110,push),(1-push)*(.5*100/110-.5))

    def test_half_line_unchanged_and_current_ties_count(self):
        h=pd.Series([1.,2.,3.]); c=pd.Series([2.])
        self.assertEqual(_push_probability(h,c,2.5),0)
        self.assertAlmostEqual(_expected_return(.6,-110),_expected_return(.6,-110,0))
        self.assertGreater(_push_probability(h,c,2),_push_probability(h,pd.Series(dtype=float),2))

    def test_all_ties_do_not_create_certain_wins(self):
        h=pd.Series([2.]*10); c=pd.Series(dtype=float)
        p,_=_market_anchored_probability(h,c,2,'OVER',.5)
        self.assertEqual(p,.5)
        self.assertGreater(_push_probability(h,c,2),0)
        self.assertLess(_expected_return(p,-110,_push_probability(h,c,2)),0)

if __name__=='__main__': unittest.main()
