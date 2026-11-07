"""Conservative search execution: unique target, then observable query-specific outcome."""
from urllib.parse import parse_qs, urlsplit

CANDIDATES = ['role=searchbox', 'role=combobox[name*="search" i]',
              'input[type="search"]', 'input[name*="search" i]',
              'input[placeholder*="search" i]', 'input[aria-label*="search" i]']

def query_in_url(url, query):
    params = parse_qs(urlsplit(url).query)
    return any(query.casefold() == value.casefold() for values in params.values() for value in values)

def execute_search(page, selectors, query, timeout_ms=3000, fallback=None):
    """Return the verified selector or None. Never retry after a submitted action."""
    if not query or not query.strip():
        return None
    for selector in dict.fromkeys(s for s in selectors if isinstance(s, str) and s):
        try:
            loc = page.locator(selector)
            if loc.count() != 1 or not loc.is_visible() or not loc.is_enabled() or not loc.is_editable():
                continue
            # A cached arbitrary input must still be semantically recognizable as search.
            if not loc.evaluate("el => el.matches('input,textarea') && (el.type === 'search' || /search/i.test([el.getAttribute('role'),el.name,el.placeholder,el.getAttribute('aria-label'),el.getAttribute('title')].join(' ')))"):
                continue
        except Exception:
            continue
        before = page.url
        try:
            loc.fill(query, timeout=timeout_ms)
            loc.press('Enter', timeout=timeout_ms)
            page.wait_for_function("([before, query]) => location.href !== before && [...new URL(location.href).searchParams.values()].some(v => v.toLocaleLowerCase() === query.toLocaleLowerCase())", arg=[before, query], timeout=timeout_ms)
            if page.url != before and query_in_url(page.url, query):
                return selector
        except Exception:
            return None
        return None
    if fallback is not None:
        try:
            proposed = fallback(page.screenshot())
        except Exception:
            return None
        if isinstance(proposed, str) and proposed:
            return execute_search(page, [proposed], query, timeout_ms)
    return None

