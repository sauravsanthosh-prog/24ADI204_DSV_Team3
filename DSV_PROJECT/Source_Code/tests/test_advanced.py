import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from attrition_lab import load_raw,clean_data
from advanced_analysis import transform_features,select_correlated,fit_pca

class AdvancedChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clean=clean_data(load_raw()).head(3000).copy()
        cls.features=transform_features(cls.clean)

    def test_labels_and_ids_cannot_change_features(self):
        changed=self.clean.copy()
        changed['Attrition']=changed.Attrition.map({'Left':'Stayed','Stayed':'Left'})
        changed['Left']=1-changed.Left
        changed['Employee ID']=-changed['Employee ID']
        other=transform_features(changed)
        pd.testing.assert_frame_equal(self.features['matrix'],other['matrix'])

    def test_scaling_and_encoding_are_finite_and_reference_dropped(self):
        f=self.features
        self.assertTrue(np.isfinite(f['matrix']).all().all())
        np.testing.assert_allclose(f['standardized'].mean(),0,atol=1e-10)
        np.testing.assert_allclose(f['standardized'].std(ddof=0),1,atol=1e-10)
        self.assertEqual(f['matrix'].shape[1],6+f['encoding'].output_columns.sum())
        self.assertNotIn('Left',f['matrix'])
        self.assertNotIn('Employee ID',f['matrix'])

    def test_pairwise_screen_drops_duplicate_and_inverse_features(self):
        x=np.arange(100,dtype=float)
        matrix=pd.DataFrame({'a':x,'copy':x,'inverse':-x,'constant':1,'independent':np.sin(x)})
        selected,decisions,_=select_correlated(matrix)
        self.assertEqual(list(selected),['a','independent'])
        self.assertEqual(decisions.action.eq('drop').sum(),3)

    def test_pca_minimal_target_and_reconstruction(self):
        result=fit_pca(self.features['matrix'])
        n=result['n_components'];v=result['variance']
        self.assertGreaterEqual(result['retained_variance'],.90-1e-10)
        if n>1:self.assertLess(v.cumulative_variance_ratio.iloc[n-2],.90)
        self.assertAlmostEqual(result['retained_variance'],v.cumulative_variance_ratio.iloc[n-1],places=10)
        model=result['model']
        np.testing.assert_allclose(model.components_@model.components_.T,np.eye(len(model.components_)),atol=1e-10)
        np.testing.assert_allclose(model.inverse_transform(result['scores']),self.features['matrix'],atol=1e-10)

if __name__=='__main__':unittest.main()
