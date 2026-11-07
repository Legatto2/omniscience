"""Offline deterministic behavior benchmark; not a browser performance benchmark."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from navigation import execute_search
from test_phase1 import Locator, Page

def run():
    outcomes = {}
    for name, count, confirmed in [('unique_confirmed',1,True),('ambiguous',2,True),('unconfirmed',1,False)]:
        page=Page({}, confirmed); page.mapping['search']=Locator(page,count=count)
        result=execute_search(page,['search'],'term')
        outcomes[name]={'reported_success': result is not None, 'submissions': page.actions}
    print(json.dumps({'fixture':'mock-page-v1', 'trials_per_scenario':1, 'outcomes':outcomes,
                      'latency_ms':None,'model_calls':0,'cost':None}, indent=2))
if __name__ == '__main__': run()
