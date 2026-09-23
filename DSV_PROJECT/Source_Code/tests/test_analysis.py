"""Meaningful regression checks for labels, row accounting and statistical behaviour."""
import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from attrition_lab import load_raw, clean_data, wilson, compare, evidence_tables, MISSING

class AnalysisChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = load_raw()
        cls.clean = clean_data(cls.raw)

    def test_row_and_target_integrity(self):
        d = self.raw.drop_duplicates().reset_index(drop=True)
        self.assertEqual(len(self.clean),len(d))
        self.assertTrue(self.clean['Employee ID'].is_unique)
        pd.testing.assert_series_equal(self.clean.Attrition,d.Attrition)
        np.testing.assert_array_equal(self.clean['Monthly Income'],d['Monthly Income'])

    def test_only_missing_numeric_values_are_imputed(self):
        d = self.raw.drop_duplicates().reset_index(drop=True)
        for col in MISSING:
            mask = d[col].notna()
            np.testing.assert_array_equal(self.clean.loc[mask,col],d.loc[mask,col])
            self.assertFalse(self.clean[col].isna().any())
            self.assertEqual(self.clean[col+' Missing'].sum(),d[col].isna().sum())

    def test_imputation_does_not_depend_on_target(self):
        swapped = self.raw.copy()
        swapped['Attrition'] = swapped['Attrition'].map({'Left':'Stayed','Stayed':'Left'})
        for method in ['median','group_median']:
            a,b = clean_data(self.raw,method),clean_data(swapped,method)
            pd.testing.assert_frame_equal(a[MISSING],b[MISSING])

    def test_conflicting_id_is_not_silently_dropped(self):
        fixture = self.raw.drop_duplicates().head(3).copy()
        extra = fixture.iloc[[0]].copy(); extra['Monthly Income'] += 1
        with self.assertRaises(ValueError): clean_data(pd.concat([fixture,extra],ignore_index=True))

    def test_wilson_known_values_and_boundaries(self):
        lo,hi = wilson(50,100)
        self.assertAlmostEqual(lo,0.4038315,places=6)
        self.assertAlmostEqual(hi,0.5961685,places=6)
        self.assertAlmostEqual(wilson(0,100)[0],0)
        self.assertAlmostEqual(wilson(100,100)[1],1)
        self.assertTrue(np.isnan(wilson(0,0)[0]))

    def test_difference_direction_and_interval(self):
        d = pd.DataFrame({'Overtime':['Yes']*100+['No']*100,
                          'Left':[1]*70+[0]*30+[1]*20+[0]*80})
        r = compare(d,'Overtime')
        self.assertAlmostEqual(r['difference_pp'],50)
        self.assertLess(r['ci_low_pp'],50); self.assertGreater(r['ci_high_pp'],50)
        self.assertGreater(r['ci_low_pp'],0)
        d['Overtime'] = d.Overtime.map({'Yes':'No','No':'Yes'})
        inv = compare(d,'Overtime')
        self.assertAlmostEqual(inv['difference_pp'],-50)
        self.assertAlmostEqual(inv['ci_low_pp'],-r['ci_high_pp'])

    def test_gate_rejects_unreachable_sample_threshold(self):
        summary,_,_ = evidence_tables(self.raw,min_n=len(self.raw)+1)
        self.assertTrue(summary.status.eq('Needs caution').all())

if __name__ == '__main__': unittest.main()
