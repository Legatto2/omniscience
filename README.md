# Omniscience: Phase 1 research prototype

This repository retains `synapse_general.py` and `demo_runner.py`. The generalized agent keeps ambient memory and the existing live entry point. The legacy demo remains an independent, unverified demonstration and its displayed elapsed time is not a controlled benchmark.

## Setup and offline checks

Python 3.11 and Playwright for Python are required for the live agent. Install `playwright` and its Chromium browser using the official Playwright instructions. `google-generativeai` is optional for the existing Gemini ambient extraction; without it the heuristic remains available. No dependency lock was provided upstream; versions have not been validated here.

Run `python -m unittest discover -s tests -v` and `python tests/benchmark_offline.py`. On systems where the default temporary directory is unwritable, set `TEMP` and `TMP` to a writable directory. The unit tests use simulated pages. Run `python tests/browser_fixture.py` for an intercepted local Chromium fixture; it requires an installed Playwright browser.

## Search and memory

For search only, cached selectors and semantic candidates follow the same unique, visible, enabled, editable, search-labelled target validation. Submission is confirmed only when navigation changes the URL and a decoded search parameter (or the search field name) equals the requested query on the same origin. This is deliberately narrow: single-page results, POST searches, identical-URL repeats, and other legitimate searches can report failure. It does not establish that relevant results loaded. A submitted but unconfirmed action is never automatically retried. Successful verified selectors are stored per supplied domain and intent in version 1 JSON. Legacy string entries are read in memory and migrated atomically on the next verified save; unknown versions and malformed JSON raise errors without overwriting the file. Back up memory before migration. Storage is single-process and has no concurrent-writer coordination.

Vision is disabled by default. To enable it, construct `UniversalUINavigator(vision_enabled=True, vision_provider=provider)`, where the provider accepts screenshot bytes and returns a CSS selector or None. The screenshot may contain sensitive information and the caller is responsible for the provider's data handling. The proposal is untrusted and passes the same semantic validation and outcome confirmation. Vision is called only when no semantic candidate can be validated, never after a submission. No provider is included; no claim of vision recovery effectiveness is made.

## Research baseline and limits

The upstream baseline at f9dc431 had no automated tests or benchmark, selected the first matching element, and treated a submitted click as success; it printed unmeasured performance claims. `tests/benchmark_offline.py` supplies reproducible mock scenarios and reports observed outcomes, not browser latency, real-world task completion, model spending, or a comparison against other agents. A proper study requires browser fixtures and held-out sites, repeated cold/warm trials, matched tasks, recorded model calls and costs, and independent outcome labels. Do not interpret mock results as proof of production reliability or research novelty.

## Browser comparison

Run `python tests/compare_baseline.py` from a Git checkout containing upstream commit `f9dc431`. It compares one trial per scenario in an intercepted Chromium fixture. On the development machine, both versions reported success for a unique search; the upstream version also reported success for ambiguous fields and a form that did not navigate, while the current version refused both. This is a small deterministic behavior check, not a completion-rate or performance study.
