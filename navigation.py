"""Conservative search execution: unique target, then observable query-specific outcome."""
from urllib.parse import parse_qs, urlsplit

CANDIDATES = ['role=searchbox', 'role=combobox[name*="search" i]',
              'input[type="search"]', 'input[name*="search" i]',
              'input[placeholder*="search" i]', 'input[aria-label*="search" i]']

SEARCH_KEYS = {"q", "query", "search", "search_query", "searchquery", "keyword", "keywords", "k", "_nkw"}

def query_in_url(url, query, field_name=None):
    params = parse_qs(urlsplit(url).query)
    keys = SEARCH_KEYS | ({field_name.casefold()} if field_name else set())
    return any(key.casefold() in keys and query.casefold() == value.casefold()
               for key, values in params.items() for value in values)

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
            field_name = loc.get_attribute("name")
        except Exception:
            return None
        try:
            loc.fill(query, timeout=timeout_ms)
            loc.press('Enter', timeout=timeout_ms)
            page.wait_for_function("""([before, query, fieldName, keys]) => {
                const oldUrl = new URL(before), current = new URL(location.href);
                const allowed = new Set([...keys, (fieldName || '').toLowerCase()]);
                return current.href !== oldUrl.href && current.origin === oldUrl.origin &&
                    [...current.searchParams.entries()].some(([key, value]) =>
                        allowed.has(key.toLowerCase()) && value.toLowerCase() === query.toLowerCase());
            }""", arg=[before, query, field_name, list(SEARCH_KEYS)], timeout=timeout_ms)
            if (page.url != before and urlsplit(page.url).netloc == urlsplit(before).netloc
                    and urlsplit(page.url).scheme == urlsplit(before).scheme
                    and query_in_url(page.url, query, field_name)):
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

