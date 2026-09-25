import sys
from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest
SOURCE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SOURCE))

class DashboardChecks(unittest.TestCase):
    def start(self):
        return AppTest.from_file(str(SOURCE/'dashboard.py'),default_timeout=60).run()

    def test_every_chapter_renders_without_exception(self):
        app=self.start()
        self.assertEqual(len(app.exception),0)
        for page in ['Data audit','Explore groups','Evidence checks','PCA map','Next actions']:
            app.radio(key='page').set_value(page).run()
            self.assertEqual(len(app.exception),0,msg=f'{page}: {app.exception}')

    def test_filters_change_denominator_and_empty_cohort_is_handled(self):
        app=self.start();app.radio(key='page').set_value('Explore groups').run()
        total=int(app.metric[0].value.replace(',',''))
        app.multiselect(key='roles').set_value(['Education']).run()
        smaller=int(app.metric[0].value.replace(',',''))
        self.assertGreater(smaller,0);self.assertLess(smaller,total)
        app.selectbox(key='scenario').set_value('Complete case').run()
        self.assertLess(int(app.metric[0].value.replace(',','')),smaller)
        app.radio(key='distribution_kind').set_value('Violin').run()
        self.assertEqual(len(app.exception),0)
        app.multiselect(key='roles').set_value([]).run()
        self.assertEqual(len(app.exception),0)
        self.assertIn('No records',app.warning[0].value)

    def test_pca_3d_and_empty_filters(self):
        app=self.start();app.radio(key='page').set_value('PCA map').run()
        app.radio(key='pca_mode').set_value('3D').run()
        self.assertEqual(len(app.exception),0)
        app.multiselect(key='pca_roles').set_value([]).run()
        self.assertIn('No records',app.warning[0].value)

if __name__=='__main__':unittest.main()
