"""Offline browser regressions for habit lifecycle and semantic search."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright
from synapse_general import UniversalUINavigator

FORM = '<form action="/results"><label for="term">Search catalog</label><input id="term" name="term" type="text"></form>'

class BrowserRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'habits.json'
        self.page = self.browser.new_page()
        self.addCleanup(self.page.close)
        self.page.route('**/*', lambda route: route.fulfill(status=200, content_type='text/html', body=FORM))
        self.page.goto('https://fixture.test/')
    def test_labeled_field_learned_and_reused(self):
        navigator = UniversalUINavigator(str(self.path))
        # Discovery uses the accessible name, not HTML attributes.
        self.assertTrue(navigator.find_and_interact(self.page, 'fixture.test', 'search', 'first'))
        saved = json.loads(self.path.read_text(encoding='utf-8'))
        self.assertEqual(saved['version'], 1)
        self.page.goto('https://fixture.test/')
        self.assertTrue(UniversalUINavigator(str(self.path)).find_and_interact(self.page, 'fixture.test', 'search', 'second'))
        self.assertIn('term=second', self.page.url)
    def test_wrong_domain_never_submits_or_saves(self):
        navigator = UniversalUINavigator(str(self.path))
        self.assertFalse(navigator.find_and_interact(self.page, 'other.test', 'search', 'term'))
        self.assertFalse(self.path.exists())
        self.assertEqual(self.page.url, 'https://fixture.test/')
    def test_stale_habit_recovers_and_updates(self):
        self.path.write_text(json.dumps({'version': 1, 'habits': {'fixture.test': {'search': {'selector': '#missing'}}}}), encoding='utf-8')
        self.assertTrue(UniversalUINavigator(str(self.path)).find_and_interact(self.page, 'fixture.test', 'search', 'term'))
        self.assertNotEqual(json.loads(self.path.read_text(encoding='utf-8'))['habits']['fixture.test']['search']['selector'], '#missing')

if __name__ == '__main__': unittest.main()
