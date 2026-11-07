"""Optional caller-supplied vision proposals; screenshots can contain sensitive data."""
from navigation import execute_search

def recover_search(page, query, provider, *, enabled=False, timeout_ms=3000):
    """Provider receives screenshot bytes and returns a CSS selector, or None.

    Explicit enablement is required. The provider controls where image data goes.
    A proposal is untrusted and passes the ordinary search verification pipeline.
    """
    if not enabled or provider is None:
        return None
    try:
        selector = provider(page.screenshot())
    except Exception:
        return None
    if not isinstance(selector, str) or not selector:
        return None
    return execute_search(page, [selector], query, timeout_ms)
