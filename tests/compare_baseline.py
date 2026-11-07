"""Compare upstream and current navigation on fixed, intercepted browser pages."""
import ast
import json
import subprocess
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright, Page
from typing import Optional, Dict, Any
import os
from navigation import CANDIDATES, execute_search

ROOT = Path(__file__).resolve().parents[1]

def load_upstream():
    source = subprocess.check_output(['git', 'show', 'f9dc431:synapse_general.py'], cwd=ROOT, text=True, encoding='utf-8')
    tree = ast.parse(source)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'UniversalUINavigator')
    namespace = {'os': os, 'json': json, 'Page': Page, 'Optional': Optional, 'Dict': Dict, 'Any': Any,
                 'GREEN': '', 'CYAN': '', 'YELLOW': '', 'RESET': ''}
    exec(compile(ast.Module(body=[cls], type_ignores=[]), '<upstream>', 'exec'), namespace)
    return namespace['UniversalUINavigator']

SCENARIOS = {
    'unique_navigation': '<form action="/results"><input type="search" name="q"></form>',
    'ambiguous_inputs': '<form action="/results"><input type="search" name="q"><input type="search" name="q"></form>',
    'no_navigation': '<form onsubmit="event.preventDefault()"><input type="search" name="q"></form>',
}

def main():
    upstream = load_upstream()
    results = {}
    with tempfile.TemporaryDirectory() as directory, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for name, markup in SCENARIOS.items():
            results[name] = {}
            for version in ('upstream', 'current'):
                page = browser.new_page()
                page.route('**/*', lambda route: route.fulfill(status=200, content_type='text/html', body=markup))
                page.goto('https://fixture.test/')
                if version == 'upstream':
                    agent = upstream(str(Path(directory) / (name + '.json')))
                    success = agent.find_and_interact(page, 'fixture.test', 'search', 'red shoes')
                else:
                    success = execute_search(page, CANDIDATES, 'red shoes', timeout_ms=300) is not None
                results[name][version] = bool(success)
                page.close()
        browser.close()
    expected = {'unique_navigation': {'upstream': True, 'current': True},
                'ambiguous_inputs': {'upstream': True, 'current': False},
                'no_navigation': {'upstream': True, 'current': False}}
    assert results == expected, results
    print(json.dumps({'fixture': 'intercepted-browser-v1', 'trials_per_case': 1, 'reported_success': results}, indent=2))

if __name__ == '__main__': main()
