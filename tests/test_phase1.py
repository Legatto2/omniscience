import json
import tempfile
import unittest
from pathlib import Path
from habits_store import HabitStore
from navigation import execute_search, query_in_url
from vision import recover_search

class Locator:
    def __init__(self, page, valid=True, count=1): self.page, self.valid, self.n = page, valid, count
    def count(self): return self.n
    def is_visible(self): return self.valid
    def is_enabled(self): return self.valid
    def is_editable(self): return self.valid
    def evaluate(self, expression): return self.valid
    def fill(self, query, timeout): self.page.query = query
    def press(self, key, timeout): self.page.actions += 1

class Page:
    def __init__(self, mapping, confirmed=True):
        self.mapping, self.confirmed, self.actions = mapping, confirmed, 0
        self.url = 'https://example.test/'
    def locator(self, selector): return self.mapping.get(selector, Locator(self, False, 0))
    def wait_for_function(self, expression, *, arg, timeout):
        if not self.confirmed: raise TimeoutError()
        from urllib.parse import urlencode
        self.url = 'https://example.test/results?' + urlencode({'q': self.query})
    def screenshot(self): return b'image'

class PhaseOneTests(unittest.TestCase):
    def test_legacy_migration_only_after_save(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'habits.json'; original = '{"site":{"search":"input[type=search]"}}'; p.write_text(original)
            store = HabitStore(p)
            self.assertEqual(store.get('site','search'), 'input[type=search]')
            self.assertEqual(p.read_text(), original)
            store.save('site','search','input[type=search]')
            self.assertEqual(json.loads(p.read_text())['version'], 1)
            self.assertEqual(HabitStore(p).get('site','search'), 'input[type=search]')
    def test_unknown_version_rejected_without_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'h.json'; p.write_text('{"version":99,"habits":{}}')
            with self.assertRaises(ValueError): HabitStore(p)
            self.assertIn('99', p.read_text())
    def test_unique_verified_search(self):
        p=Page({}); p.mapping['a']=Locator(p)
        self.assertEqual(execute_search(p,['a'],'red shoes'), 'a')
        self.assertEqual(p.actions,1)
    def test_ambiguous_falls_back(self):
        p=Page({}); p.mapping={'a':Locator(p,count=2),'b':Locator(p)}
        self.assertEqual(execute_search(p,['a','b'],'search term'),'b')
    def test_no_retry_after_unconfirmed_submission(self):
        p=Page({},False); p.mapping={'a':Locator(p),'b':Locator(p)}
        self.assertIsNone(execute_search(p,['a','b'],'term'))
        self.assertEqual(p.actions,1)
    def test_url_query_must_match(self):
        self.assertFalse(query_in_url('https://example.test/?q=other','term'))
        self.assertTrue(query_in_url('https://example.test/?q=red+shoes','red shoes'))
    def test_vision_opt_in_and_validation(self):
        p=Page({}); p.mapping['a']=Locator(p)
        calls=[]
        def provider(image): calls.append(image); return 'a'
        self.assertIsNone(recover_search(p,'term',provider))
        self.assertEqual(calls,[])
        self.assertEqual(recover_search(p,'term',provider,enabled=True),'a')
    def test_invalid_semantics_rejected(self):
        p=Page({}); p.mapping['a']=Locator(p,False)
        self.assertIsNone(execute_search(p,['a'],'term'))
        self.assertEqual(p.actions,0)

if __name__ == '__main__': unittest.main()
