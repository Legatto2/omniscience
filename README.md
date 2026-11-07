<div align="center">

<img src="docs/images/omniscience-hero.webp" alt="Abstract eye made of connected nodes and browser windows" width="100%">

# OMNISCIENCE

**See. Hear. Speak. Remember. Act.**

*Toward an AI companion that understands context and acts with purpose.*

[The vision](#the-grand-vision) · [The research](#the-research-question) · [Prototype](#how-the-prototype-works) · [See the demo](#a-glimpse-of-the-demo) · [Run the checks](#setup-and-offline-checks)

</div>

---

Omniscience is an experimental AI research project exploring a more capable digital companion: one that can perceive its surroundings, carry context forward, communicate naturally, and help people act in the digital world. The browser agent is our first research environment and the foundation for testing that larger idea.

## The grand vision

Imagine mentioning a book in conversation, then later saying, “Find that book we talked about.” An assistant could recall the conversation, check current information from an authorized source, search for the right title, and explain what it found. Over time, it could also learn which steps reliably complete familiar tasks.

The long-term goal is to bring these abilities together:

- **See:** understand screens and, eventually, visual surroundings; track relevant objects and changes over time.
- **Hear:** learn useful context from ambient speech when listening is explicitly enabled, so the assistant can understand references made later.
- **Speak:** communicate naturally, ask when context is uncertain, and explain what it has done.
- **Remember:** maintain personal context and reusable procedures, alongside world knowledge refreshed from authorized data sources—including potential Google integrations where access is available.
- **Act and verify:** use that context to help with tasks, check outcomes, learn from experience, and seek approval for consequential actions.

“See, hear, and speak like we do” expresses the intended experience; it is not a claim that the system has human perception, understanding, or consciousness. Continuously updating memory is also distinct from retraining a model: the intended system may retrieve and revise information without changing model weights.

Ambient listening and external data access require explicit user control, clear recording indicators, appropriate treatment of bystanders, and transparent choices about storage, deletion, and sharing. Sources need provenance, freshness, and access controls; the project does not assume unrestricted access to Google's proprietary data. These are design requirements for future work, not guarantees of the current prototype.

> **Research vision, not a product claim:** Live microphone capture, spoken interaction, continuously refreshed external knowledge, and a persistent visual state model are not implemented in this repository today.

## The research question

Can an agent combine personal context, current knowledge, and learned procedures to carry out useful tasks reliably—and know when its memory or understanding is uncertain? Our first measurable step is to test verified browser-task reuse and recovery as interfaces change.

Omniscience explores a two-path approach:

- **Familiar tasks:** retrieve a previously verified, site-scoped habit and validate its target before using it.
- **Unfamiliar or changed interfaces:** discover targets through browser semantics and, where explicitly enabled, accept a proposal from a vision provider. Proposed actions still need validation and outcome confirmation.

The broader direction includes a persistent representation of interface objects and state, and experiments with predicting outcomes before actions. These are research goals, not capabilities demonstrated by the current code. Omniscience does not claim human-like understanding or a proven advantage over other agents.


## How the prototype works

```mermaid
flowchart LR
    A["Search intent"] --> B{"Known habit?"}
    B -- Yes --> C["Validate cached target"]
    B -- No --> D["Discover a semantic target"]
    C -- Stale or invalid --> D
    D -- No valid target --> V["Optional provider proposal"]
    D --> E["Validate target"]
    V --> E
    C -- Valid --> F["Submit search"]
    E --> F
    F --> G{"Outcome confirmed?"}
    G -- Yes --> H["Save verified habit"]
    G -- No --> I["Report unconfirmed"]
```

This diagram describes the current search path. Vision is an optional provider interface; proposals are validated using the same search checks. An unconfirmed submission is not retried automatically.

## A glimpse of the demo

![Results page from a recorded run of the original Project Synapse demo](docs/images/legacy-demo-results.webp)

*Historical demo footage: the original demo reached a results page for “Gladiator 2.” This is a single observed run of the legacy demo, not a benchmark or validation of the current verified workflow.*

## Current status

The repository is an early prototype. Its implemented verified workflow is limited to search: it discovers or retrieves a search field, checks that the target is actionable and unambiguous, submits the query, and checks for a narrowly defined URL outcome before saving a habit. It also preserves the original ambient-memory extraction, recall, and demonstration entry points. The legacy demo is independent of the verified search workflow; its displayed elapsed time is not a controlled benchmark.

The current vision interface is an opt-in extension point that accepts a caller-supplied provider; no vision model is bundled. The project does not yet provide general-purpose task planning, a persistent visual state graph, predictive simulation, or comprehensive safeguards for sensitive actions. Treat it as a research prototype, not an autonomous production agent.

## How we will evaluate it

Evaluation should compare familiar-task reuse, first-time discovery, and recovery under controlled interface changes using the same tasks and explicit completion criteria. Report successful completion and false positives alongside latency, model calls, cost when known, and failure cases. Use repeatable local fixtures first, then evaluate on held-out sites and realistic workflows. The existing checks are small fixture tests, not evidence of broad reliability or performance gains.

## Setup and offline checks

Python 3.11 and Playwright for Python are required for the live agent. Install `playwright` and its Chromium browser using the official Playwright instructions. `google-generativeai` is optional for the existing Gemini ambient extraction; without it the heuristic remains available. No dependency lock was provided upstream; versions have not been validated here.

Run the offline checks from the repository root:

```bash
python -m unittest discover -s tests -v
python tests/benchmark_offline.py
```

On systems where the default temporary directory is unwritable, set `TEMP` and `TMP` to a writable directory. The unit tests use simulated pages. Run `python tests/browser_fixture.py` and `python tests/browser_regression.py` for intercepted local Chromium fixtures; they require an installed Playwright browser.

## Search and memory

For search only, cached selectors and semantic candidates follow the same unique, visible, enabled, editable, search-labelled target validation. Submission is confirmed only when navigation changes the URL and a decoded search parameter (or the search field name) equals the requested query on the same origin. This is deliberately narrow: single-page results, POST searches, identical-URL repeats, and other legitimate searches can report failure. It does not establish that relevant results loaded. A submitted but unconfirmed action is never automatically retried. The supplied domain must match the open page authority, including any explicit port. Successful verified selectors are stored per domain and intent in version 1 JSON. Legacy string entries are read in memory and migrated atomically on the next verified save; unknown versions and malformed JSON raise errors without overwriting the file. Back up memory before migration. Storage is single-process and has no concurrent-writer coordination.

Vision is disabled by default. To enable it, construct `UniversalUINavigator(vision_enabled=True, vision_provider=provider)`, where the provider accepts screenshot bytes and returns a CSS selector or None. The screenshot may contain sensitive information and the caller is responsible for the provider's data handling. The proposal is untrusted and passes the same semantic validation and outcome confirmation. Vision is called only when no semantic candidate can be validated, never after a submission. No provider is included; no claim of vision recovery effectiveness is made.

## Research baseline and limits

The upstream baseline at f9dc431 had no automated tests or benchmark, selected the first matching element, and treated a submitted click as success; it printed unmeasured performance claims. `tests/benchmark_offline.py` supplies reproducible mock scenarios and reports observed outcomes, not browser latency, real-world task completion, model spending, or a comparison against other agents. A proper study requires browser fixtures and held-out sites, repeated cold/warm trials, matched tasks, recorded model calls and costs, and independent outcome labels. Do not interpret mock results as proof of production reliability or research novelty.

## Browser comparison

Run `python tests/compare_baseline.py` from a Git checkout containing upstream commit `f9dc431`. It compares one trial per scenario in an intercepted Chromium fixture. On the development machine, both versions reported success for a unique search; the upstream version also reported success for ambiguous fields and a form that did not navigate, while the current version refused both. This is a small deterministic behavior check, not a completion-rate or performance study.
