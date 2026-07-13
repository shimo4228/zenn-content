---
title: "Fault Injection TDD Found 3 Silent Failures in My LLM Agent"
emoji: "🧪"
type: "tech"
topics: ["llm", "testing", "pytest", "hypothesis", "agents"]
published: true
description: "Turn production incident history into a fault catalog, inject those faults deterministically in pytest (hypothesis + responses, no daemon, no proxy), and assert how the system should fail. First application surfaced 3 silent failures that ~1800 existing tests had missed."
---

Pipelines with an LLM in the loop keep hitting walls like these:

- The LLM returns JSON in a subtly different shape. Parsing succeeds, but the result silently comes back empty
- A local LLM's response was cut off mid-generation (`done_reason=length`) and you only notice days later
- The log only says `outcome="error"`, so you can't tell whether it was a rate limit or a timeout

What they have in common: **every test passes, yet production breaks silently**. Processing doesn't stop, no exception is raised — the results, or the records of them, quietly degrade. In this article I call this a silent failure.

The local-LLM CLI agent I operate hit this family of failures 5 times. All 5 slipped past the tests I had beforehand and were only diagnosed after the fact. So I adopted this workflow: build a fault catalog (a taxonomy of failures) from the history of production incidents, write tests that deliberately inject those faults *first*, and land the minimal guard that makes them pass in the same PR. Taxonomically, this is **fault injection testing × TDD**. What I borrowed — and deliberately didn't borrow — from chaos engineering (the practice of injecting failures on purpose to verify resilience), which inspired the approach, is laid out in the body.

The first application found 3 silent failures that my ~1800 existing tests had missed.

> **What you'll get from this article**: a pattern for adding fault injection testing to a single-process Python app — no daemon, deterministic, pytest-native (fault catalog → RED → GREEN) — plus the details of the 3 silent failures the first application actually surfaced

## Prerequisites

- Python 3.13 / pytest 9.0 (at time of verification; no bleeding-edge features are used, so nearby versions should work)
- [hypothesis](https://hypothesis.readthedocs.io/en/latest/) 6.156.6 / [responses](https://github.com/getsentry/responses) 0.26.0 (both added as dev dependencies)
- Target: a single-process Python app that calls an LLM server (Ollama etc.) via `requests`
- The LLM call sits behind a swappable layer such as a Protocol (if it doesn't, carving out that layer is step zero)

This article is a sequel to my previous one, ["Why Did My Agent Decide That? 3 Observability Patterns"](https://dev.to/shimo4228/why-did-my-agent-decide-that-3-observability-patterns-ami). If that one was about **recording** the agent's decisions, this one is about **asserting on** that recording channel — and **injecting faults up front**. It stands alone, though.

## Chaos engineering was the inspiration; fault injection testing is what I adopted

My agent operates autonomously on a social network (Moltbook), continuously. As long as it keeps running, I can't know in advance which failure it will meet next. Searching for a way to build "operations resilient to unforeseen failures," I arrived at chaos engineering.

But measured against the five advanced principles of the canonical [Principles of Chaos Engineering](https://principlesofchaos.org/), I did not follow it verbatim.

| Canonical principle | This work |
|---|---|
| Build a Hypothesis around Steady State Behavior | ○ Adopted (asserts against the execution-log (telemetry) channel) |
| Vary Real-world Events | △ Half (faults come from incident history, but injection is a deterministic replay of a known catalog) |
| Run Experiments in Production | ✕ Rejected |
| Automate Experiments to Run Continuously | △ CI runs them automatically, but derandomized — a regression test that pins the known, not an experiment that explores the unknown |
| Minimize Blast Radius | ○ Adopted in extreme form (injection happens inside tests, so production impact is zero) |

I rejected production experiments for 2 reasons. First, the target is a single local process — there is no "redundant fleet of instances" to kill in the first place. Second, the logs the agent accumulates are primary data that can't be regenerated; random injection in production risks corrupting them. I deferred random exploration to keep CI from going flaky.

The core of chaos engineering is not "testing" (asserting known expected behavior) but "**experimentation**" (discovering unknown weaknesses) — so once production experiments and random exploration are out, it can no longer be called chaos engineering. As stated up front, the classification is fault injection testing × TDD. What I borrowed from chaos engineering is exactly 2 ideas: "build the failure catalog from real-world events" and "assert steady state through an observation channel."

Tooling-wise, I also skipped the distributed-systems staples and built on pytest. This was the conclusion of pre-adoption external research.

| Candidate | Verdict | Reason |
|---|---|---|
| chaostoolkit / toxiproxy | Rejected | Declarative experiment runner / resident network proxy. Built for distributed topologies; the scale of the target doesn't match a single local process |
| pytest fault-injection plugins | Rejected | Nothing usable exists (e.g. pytest-disrupt is a TODO-only scaffold) |
| [agent-chaos](https://github.com/deepankarm/agent-chaos) | Reference only | Conceptually the closest, but coupled to the Anthropic SDK / DeepEval / pydantic-ai, with no pytest integration and no local-backend support |
| hypothesis + responses + a hand-rolled injection backend | **Adopted** | Sits on the existing test infrastructure (pytest) with just 2 dependencies |

That settled the approach: **inject faults deterministically inside tests**. No daemon, no proxy — pytest itself is the execution environment.

The 2 elements I deferred (exploration, experimentation) are not discarded; they remain as **the entry points for extending this toward chaos engineering later** — a two-tier setup where PR CI stays deterministic while a nightly run randomizes with seed recording (any failing sequence found gets reproduced from the seed and pinned with `@example`), plus sandbox experiments running the real pipeline in random-injection mode. This pilot leaned deterministic because the state of "even the known incident history isn't asserted" had to be fixed first. Once the known holes are plugged, those 2 entry points are where I'll expand.

## The pattern — the fault catalog becomes the test spec

The workflow is 3 steps.

1. **Catalog**: classify the history of production incidents into fault classes (failure taxonomies) and diff them against existing tests. The untested classes become the fault catalog
2. **RED**: for each fault, assert in a test how the system **should** behave when it's injected. The current implementation fails it (this is TDD's RED)
3. **GREEN**: land the minimal guard that passes the test, in the **same PR** as the test

The point is that the fault catalog doubles as a spec. Desired behaviors — "a timeout should leave `error_kind=timeout` in telemetry," "malformed-shape JSON should abstain with a reason code" — get pinned down as executable tests.

The only difference from ordinary TDD is where the inputs come from. Instead of writing tests from functional requirements, you **write tests from incident history** — everything else reuses the RED → GREEN discipline as-is.

## Build the fault catalog from incident history, not imagination

If you enumerate "which faults to inject" from imagination, you tend to mass-produce tests for failures that never actually happen. I started from 5 past production incidents (silent truncation from context-length overflow, mid-generation cutoff with `done_reason=length`, deduplication failing to fire, an external API rate limit, and a scraping target turning into a CAPTCHA) and swept for "failures in the same family that existing tests don't cover."

One caveat: the 5 incidents and the fault classes are not 1:1. What I extracted from the history is the shared family — "when the LLM or external I/O returns something unexpected, the pipeline silently degrades" — and from that family I derived the 5 classes that **existing tests didn't cover**.

Here are the resulting 5 classes.

| # | Fault class | State of existing tests |
|---|---|---|
| F1 | Read-timeout mid-generation | Only `ConnectionError` covered. Mid-stream timeout untested |
| F2 | Embedding API failures — transport-level (429, timeout) and content-invalid success responses (mismatched dimensions, missing rows) | Untested |
| F3 | Syntactically valid JSON that violates the expected schema (wrong top-level type, wrong keys, non-string elements) | Untested |
| F4 | HTTP 429 from the LLM server itself | Only covered on a different external API client. LLM backend side untested |
| F5 | Flapping (alternating / consecutive success-failure sequences) | Only single failure→recovery covered |

Before and after:

| Metric | Before | After |
|---|---|---|
| Tests directly injecting the fault classes | 0/5 (per the table above, only partial coverage of adjacent cases) | 5/5 (32 deterministic fault injection tests) |
| Telemetry failure-type discrimination | None (everything is `outcome="error"`) | 7 kinds of `error_kind` |
| Observability of extraction failures | Silently missing | 3 reason codes + per-reason aggregate summary |
| Full suite | — | 1832 passed / 1 skipped |

The test count of 32 is measured with `pytest --collect-only` (every number in this article was re-measured at the time of writing).

## Implementation — 2 replacement points and a determinism discipline

### Pin injection to 2 existing seams

Injecting faults requires a seam (a joint where the test side can swap the implementation without rewriting production code). I used only 2 existing ones and decided to **add zero injection hooks to production code**. The pipeline under test does not know it is being tested.

1. **The LLM backend Protocol** — implement a `ChaosBackend` on the test side and swap it in
2. **The requests HTTP layer** — fake HTTP responses with the `responses` library

`ChaosBackend` is driven by a schedule — a list of "which fault fires on which call." The chaos in class and file names is a leftover from the naming at inspiration time. Also, `FAULT_VOCABULARY` in the code is the minimal unit of injection (primitives), at a different granularity from the F1–F5 fault classes — one class is tested through combinations of several primitives.

```python:tests/chaos.py (excerpt, simplified — see the public skill in Related Links for the full version)
# Fault vocabulary is an ordered tuple (unordered would break seed-derived determinism)
FAULT_VOCABULARY = (OK, NONE, EMPTY, EXC_TIMEOUT, EXC_CONNECTION, TRUNCATED, SHAPE_VIOLATION)

@dataclass
class ChaosBackend:  # conforms to the LLMBackend Protocol
    schedule: List[str] = field(default_factory=list)
    calls: List[dict] = field(default_factory=list)

    @classmethod
    def from_seed(cls, seed: int, n: int, weights=None) -> "ChaosBackend":
        rng = random.Random(seed)
        vocab = list(weights.keys()) if weights else list(FAULT_VOCABULARY)
        wts = list(weights.values()) if weights else None
        return cls(schedule=rng.choices(vocab, weights=wts, k=n))

    def generate(self, prompt, system, num_predict, format, *, temperature=1.0, think=False):
        idx = len(self.calls)
        self.calls.append({"prompt": prompt, "num_predict": num_predict})
        fault = self.schedule[idx] if idx < len(self.schedule) else OK
        if fault == NONE: return None
        if fault == EXC_TIMEOUT: raise requests.exceptions.ReadTimeout("chaos")
        if fault == TRUNCATED: return BackendResult(text=self._ok_text(idx), finish_reason="length")
        ...
```

A schedule can be built as an explicit list or derived from a seed — either way, **you can inspect its contents before the run**. This is not "break things randomly"; it's "breaking under this exact sequence is the spec."

### Run hypothesis under a deterministic profile

Instead of enumerating fault combinations by hand, I use property-based testing (asserting properties that must hold for any input, rather than individual input/output examples). To keep CI from going flaky, though, hypothesis is pinned to deterministic mode.

```python:tests/conftest.py (excerpt)
# database=None only disables the example DB. The constants/unicode caches
# need HYPOTHESIS_STORAGE_DIRECTORY relocated (before hypothesis is imported)
os.environ.setdefault("HYPOTHESIS_STORAGE_DIRECTORY", str(_TEST_HOME / ".hypothesis"))
from hypothesis import settings
settings.register_profile("ci", derandomize=True, max_examples=50, deadline=None, database=None)
settings.load_profile("ci")
```

`derandomize=True` generates the same case sequence every run. I verified this by running the full fault injection suite twice in a row and confirming identical output.

The other determinism rule: **latency faults are expressed by injecting a `ReadTimeout` exception, not by real sleeps**. On this call path, the observable consequence of a timeout reduces entirely to "catch and handle `ReadTimeout`," so within that scope exception injection verifies the same thing — and the tests run in 0 seconds. The real-sleep-plus-short-timeout approach goes flaky, so I avoided it. Note that **behaviors that only surface in real time cannot be verified this way** — e.g. cleanup of partial output mid-stream — so if that's your target, you need separate measures.

### Writing RED — assert the desired guard behavior first

Here is the RED for F3 (valid JSON, wrong shape).

```python:tests/test_distill_chaos.py (excerpt)
class TestParsePatternsShapeViolationFuzz:
    @given(raw=non_patterns_json())
    @example(raw='{"patterns": [123]}')   # pins the real str() promotion bug
    @example(raw="null")                  # pins the json.loads("null") is None trap
    def test_wrong_shape_abstains_with_no_patterns(self, raw):
        patterns, mode = _parse_patterns(raw)
        assert mode == "shape_violation"
        assert patterns == []
```

`@given` asserts the property "any shape-violating JSON should cause abstention," and `@example` pins known failure shapes as permanent regression tests. Those 2 `@example`s are exactly silent failures ① and ② in the next section.

## The 3 silent failures the first application surfaced

The moment I wrote the RED tests, 3 holes in the existing implementation were exposed. ① and ② are the kind where the processing result silently degrades; ③ is on the observation-channel side — the failure itself gets recorded, but the type information needed for root-cause analysis is silently lost.

### ① Numbers promoted to strings let schema violations sail through

- **Symptom**: when the LLM returned non-string elements like `{"patterns": [123]}`, the old implementation stringified each element with `str(item)`, so `"123"` could pass as a legitimate pattern
- **Why it's silent**: the JSON is valid, so parsing succeeds, and `str()` promotion raises nothing. No trace of the schema violation is left anywhere
- **Guard**: require `isinstance(item, str)` on every element; on violation, abstain with the `shape_violation` reason code. Regression pinned with `@example(raw='{"patterns": [123]}')`

### ② `json.loads("null")` returns `None`

- **Symptom**: when the response body is JSON `null`, `json.loads` returns `None` without raising. The old implementation used "parse result is `None` = parse failed" as its check, so valid JSON was treated as a parse failure and misrouted into a fallback path (bullet-list text scanning) it should never have entered
- **Why it's silent**: the fallback path legitimately exists as a rescue for non-JSON responses, so a misroute is indistinguishable in the logs from a normal fallback
- **Guard**: introduce an identity sentinel, `_JSON_PARSE_FAILED = object()`, separating "parsing failed" from "`None` was parsed" at the type level

### ③ Telemetry flattens every failure type into `error`

- **Symptom**: whether it was a 429, a timeout, a connection failure, or a bad body, telemetry only recorded `outcome="error"`, making offline failure analysis impossible
- **Why it's silent**: the error itself is recorded, so "something failed" is visible. What's flattened is the **type** — a gap you can't notice until you actually attempt an incident investigation
- **Guard**: add `_classify_request_error` to classify exceptions, and add an `error_kind` field to failure rows only (7 kinds: `timeout` / `connection` / `http_<status>` / `bad_json` / `bad_url` / `request_error` / `backend_exception`). The change is additive — the existing `outcome` value set is untouched — so analysis code over past logs keeps working

What the 3 share: they are **abnormal paths wearing a happy-path face**. Bugs that raise exceptions get caught by ordinary tests, but all 3 of these "run to completion while the result or the record goes quietly wrong" — no amount of extra happy-path tests would have caught them. Only RED tests that inject faults and assert the desired way of failing expose these holes.

:::details 2 gotchas (hypothesis cache / circuit breaker × property tests)

**`.hypothesis/` appears even with `database=None`**

Even with `database=None` in the profile, caches like `.hypothesis/constants/` show up at the repo root. As the [settings reference](https://hypothesis.readthedocs.io/en/latest/reference/api.html) says, `database=None` only suppresses the example DB; the constants cache and friends are written unconditionally under `HYPOTHESIS_STORAGE_DIRECTORY`. The fix is to point that environment variable at a test tempdir **before** importing hypothesis (included in the code sample above).

**The circuit breaker breaks property-test predictions**

I asserted the property "success count = number of OKs in the schedule," and it broke only on schedules with 5 consecutive failure faults. The cause was the circuit breaker in production code (a mechanism that cuts off calls after consecutive failures; in this project it opens after 5 in a row). Once the breaker opens, subsequent OK calls never reach the backend, so the exact-count property can't hold even though the behavior is correct. I handled it in 2 layers: exclude breaker-tripping schedules from the exact-count property via a `trips_circuit()` filter, and keep a weaker property — "no schedule ever crashes" — over all schedules.

:::

## Wrap-up — turning post-hoc debugging into up-front spec

- Silent failures don't get caught by happy-path tests. Only tests that **inject faults and assert the desired way of failing** catch them
- Build the fault catalog from **production incident history**, not imagination. 5 incidents → 5 untested fault classes → 32 deterministic fault injection tests
- For a single-process local LLM app, no daemon or proxy needed: **hypothesis + responses + a swappable backend** sit right on top of pytest
- The determinism discipline (`derandomize` / seed-derived schedules / no real sleeps) removes the 2 big flakiness sources — randomness and real time — from injection tests (measured: identical output across 2 consecutive runs)
- Land the guard in the **same PR** as the test. The fault schedule is the spec; the guard is the implementation that satisfies it
- Chaos engineering is the inspiration, not the classification. What I borrowed is 2 things — "build the catalog from real-world events" and "assert steady state through an observation channel" — while production experiments and unknown-space exploration are deliberately deferred (nightly randomization and sandbox experiments are the entry points for extending toward chaos)

The pattern from this work (fault vocabulary, ChaosBackend, hypothesis profile, RED templates) is published as a generalized Claude Code skill. If you want to bring this into your own pipeline, that's the entry point.

## Related Links

- [chaos-tdd-fault-injection](https://github.com/shimo4228/chaos-tdd-fault-injection) — the public skill generalizing this article's pattern (called "chaos-TDD" in the repo and its ADRs)
- [ADR-0077: Chaos-TDD Fault Injection](https://github.com/shimo4228/contemplative-agent/blob/main/docs/adr/0077-chaos-tdd-fault-injection.md) — primary source for the design decisions (English; a Japanese version sits in the same directory)
- [Previous article: Why Did My Agent Decide That? 3 Observability Patterns](https://dev.to/shimo4228/why-did-my-agent-decide-that-3-observability-patterns-ami)
- [Building an Autonomous Agent on an M1 Mac, on Purpose](https://zenn.dev/shimo4228/articles/small-llm-by-choice) — hub of the small-LLM series this article belongs to (Japanese)
- [hypothesis documentation](https://hypothesis.readthedocs.io/en/latest/) / [responses](https://github.com/getsentry/responses)
- [Chaos Toolkit](https://chaostoolkit.org/) / [toxiproxy](https://github.com/Shopify/toxiproxy) — chaos tools for distributed systems (not adopted here due to the mismatch in target scale)
- [agent-chaos](https://github.com/deepankarm/agent-chaos) — prior OSS for chaos engineering on AI agents (prior art referenced for fault classification)
- [Author's GitHub](https://github.com/shimo4228) — other repositories and tools
