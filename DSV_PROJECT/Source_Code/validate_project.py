"""Run data, PCA and dashboard regression tests and record actual results."""
import datetime
import json
from pathlib import Path
import sys
import unittest

def run():
    source=Path(__file__).resolve().parent
    suite=unittest.defaultTestLoader.discover(str(source/'tests'))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    summary={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
        'skipped':len(result.skipped),'passed':result.wasSuccessful(),
        'scope':'Data integrity, target exclusion, scaling, PCA reconstruction and Streamlit interactions'}
    (source.parent/'Reports'/'validation_results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return 0 if result.wasSuccessful() else 1

if __name__=='__main__':sys.exit(run())
