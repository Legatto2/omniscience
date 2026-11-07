"""Local intercepted browser fixture; no network access is required."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright
from navigation import execute_search, CANDIDATES

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.route('**/*', lambda route: route.fulfill(status=200, content_type='text/html', body='<form action="/results"><label>Search <input type="search" name="q"></label></form>'))
        page.goto('https://fixture.test/')
        selector = execute_search(page, CANDIDATES, 'red shoes')
        assert selector is not None, 'search was not confirmed'
        assert 'q=red+shoes' in page.url, page.url
        print('PASS: Chromium intercepted fixture confirmed search:', selector)
        browser.close()
if __name__ == '__main__': main()
