---
title: "What Do My AI Agent's Logs Look Like in OpenTelemetry?"
emoji: "🔌"
type: "tech"
topics: ["opentelemetry", "observability", "jaeger", "llm"]
published: false
description: "I converted my AI agent's existing audit logs into OpenTelemetry traces after the fact — no runtime SDK, no Collector, two dependencies — and sorted out which parts of OTel are worth borrowing and which you can skip."
tags: opentelemetry, observability, jaeger, llm
---

> **What this article covers**: what you can see when you plug homegrown logs into OpenTelemetry. I convert them to OpenTelemetry format, visualize them, and sort out which elements are worth borrowing and which you can pass on.

I wanted to bring OpenTelemetry to my AI agent (telemetry = the standard machinery for recording and emitting data about a system's behavior; OTel from here on). The typical adoption path is to embed the SDK in the application itself, emit telemetry as it runs, and keep shipping it to a monitoring backend via a Collector (a resident process that receives, transforms, and forwards). But maybe you've hit walls like these:

- **Running an SDK and a Collector around the clock is heavy for a personal-scale agent.** There's no ops team watching a monitoring dashboard
- **I already have my own structured logs.** I don't want to instrument the same information twice
- **The standard for which attribute names to record LLM calls under (the GenAI semantic conventions) is still in development.** The spec may still move, so it's hard to judge how far to lean on it

[Contemplative Agent](https://github.com/shimo4228/contemplative-agent), the agent I operate, was in exactly this situation. It's a local-LLM agent that autonomously writes posts and comments on Moltbook (a social network where AI agents post and comment on each other). The text it reads from the feed is written by other agents, and prompt injection (smuggling instructions into a post body to steer the agent reading it) is a daily occurrence — an environment where input cannot be trusted.

When the agent misbehaves in this environment, investigating the cause requires being able to trace, precisely and after the fact, "what it read from outside and what it emitted at that moment." So I had designed all external input/output to be kept in full in an audit log (an append-only record for reproducing past decisions exactly as they happened). The "own structured logs" in the second wall above is this audit log.

At the same time, nobody in my environment watches telemetry continuously. What I need is "the ability to examine past runs in a standard UI when something is worth investigating." If that's the requirement, the telemetry doesn't have to be flowing in real time.

So this article does two things.

1. **Instead of putting OTel into the production runtime, I built an after-the-fact conversion as an experiment.** It takes the audit logs I already have, converts them into traces (a record of one processing run as a collection of timestamped intervals) after the fact, and ships them over OTLP (OTel's standard transport protocol) for visualization
2. **I compared my log schema against the OTel standard and added the 2 fields it was missing to the agent's own logs**: `run_id` and `session_id`, which identify a run

The first is a small conversion script — zero changes to the agent body, two dependencies. My local logs became visible as a waterfall (the chart that stacks processing intervals along a timeline) in Jaeger (an OSS trace viewer). On a day that had an incident, the picture tells you the moment you open it.

This article is a sequel to my previous piece, ["Why Did My Agent Decide That? 3 Observability Patterns"](https://dev.to/shimo4228/why-did-my-agent-decide-that-3-observability-patterns-ami). There I wrote that what traces and metrics tell you by default stops at "what the request did." This is the continuation: **what, then, can homegrown logs and the OTel standard actually connect?** — answered by doing the conversion for real. It also reads fine on its own.

## Prerequisites

- Conversion target: append-only JSONL (one JSON per line) logs the agent has already written. Three kinds: LLM call telemetry / API audit / CAPTCHA solver audit
- Python 3.10+, uv for package management
- Only two dependencies: `opentelemetry-sdk` + `opentelemetry-exporter-otlp-proto-http` (both on the conversion-script side; nothing is added to the agent itself)
- Viewer: Jaeger v2.19.0 (single binary; no Docker required, storage is in-memory)
- Signals: traces only (of OTel's three signals, metrics and logs are out of scope this time)
- The conversion script is public: [contemplative-agent-otel](https://github.com/shimo4228/contemplative-agent-otel) — a small implementation, about 800 lines in total, built on the assumption that you swap in `records.py` (log loading and normalization) / `mapping.py` (the attribute-name mapping table) for your own log format

The processing flow is 5 steps.

1. Read the already-written JSONL logs
2. Normalize the 3 log kinds into a common record (`records.py`)
3. Attach standard attribute names to each record and convert it into a span (one interval of a trace) (`mapping.py`)
4. Send to Jaeger over OTLP/HTTP
5. Check the waterfall and the attributes in the Jaeger UI

## I decided whether to adopt OTel by asking "who reads the telemetry?"

Put OTel into the agent, or pass? I organized this decision around a single question: "who is going to read that telemetry?" The reason is that OTel traces and my audit log, even when they record the same event, have **different readers (consumers)**. Take one LLM call: on the trace side, what you want to see is the model name, token counts, duration, and whether it errored. On the audit-log side, what you need is the prompt body itself, the caller, and the identifiers used for reproduction.

| | OTel traces | My audit log |
|---|---|---|
| Primary reader | People watching dashboards; alerting | People investigating incidents; the replay script used for reproduction |
| Prompt and other bodies | **Not recorded by default** (opt-in) | **Stored in full** (base64 + sha256) |
| Nature of the data | May be sampled; may be volatile | Append-only; every record; never deleted |
| Question it answers | "What's slow or broken right now?" | "Why did that decision come out the way it did?" |

The right column is not a property of audit logs in general — it's a design I chose because my goal is offline reproduction of incidents. Your logs may well not store everything. What generalizes is the yardstick: **different consumers mean different retention policies.**

The emblematic case is body text. The GenAI semantic conventions specify that prompt and response bodies are **not recorded by default** (they end up on a viewer's screen, so not carrying sensitive data is the default). My audit log does the **exact opposite: full retention**. In incident investigation, without "the exact bytes the decision saw," you can't reproduce it offline.

So this isn't a question of which one is right: **same event, different consumers, opposite retention policies.** Once you frame it this way, the choice stops being binary.

1. Put OTel into the runtime (if someone reads telemetry in real time)
2. Do nothing
3. **Convert existing logs into traces after the fact** — get the connection to the standard vocabulary, and the visualization, without touching the runtime

This article is an implementation of option 3.

That said, option 3 only held up because two conditions happened to be true for me: nobody reads telemetry in real time, and the incident-investigation reader was already well served by a thorough audit log. If either is missing, the answer changes. Even with no monitoring team, if you don't have structured logs yet, going straight for option 1 (the runtime SDK) is probably faster. "No monitoring team = no OTel" is not a general rule.

You might also wonder: "isn't using only part of the standard just cherry-picking the spec?" OTLP is a public protocol, and the semantic conventions are an agreement on attribute names. You don't have to instrument the app with the SDK — any program that speaks OTLP can feed data in. This is a usage the standard anticipates, and this article's conversion script simply uses the OTel SDK as "a library for offline export."

## What I borrowed from OTel, and what I passed on

Before getting into the implementation, here's how I judged each element of OTel, up front. The biggest lesson this time was that it's not an all-or-nothing "adopt the standard or don't" — **you can pick borrow-or-pass per element.**

| OTel element | Verdict | Why |
|---|---|---|
| GenAI semantic conventions vocabulary (`gen_ai.*`) | ✅ Adopt | External tools and people can read it without explanation. Copying attribute names costs zero dependencies |
| Run-ID machinery (trace ID / session ID equivalents) | ✅ Adopt (implemented `run_id` / `session_id` in the logs) | One field turns trace reconstruction from estimation into measurement |
| OTLP (transport protocol) | ✅ Adopt (as the exit of the offline conversion) | A common language every viewer speaks. Costs only 2 packages |
| Runtime SDK instrumentation | ❌ Pass | Would double-instrument alongside the existing audit log, and add dependencies to the agent |
| Running a resident Collector | ❌ Pass | Heavy for a single process at personal scale. On-demand conversion when needed is enough |
| Bodies not recorded by default (redaction) | Partial | Followed on the trace side (don't carry untrusted text onto the screen). The audit log does the opposite — full retention, needed for offline reproduction |
| Importing attribute names from the semconv package | ❌ Pass | Import paths are still unstable while in development, so attribute names are self-managed as string constants |

Passing on an element doesn't mean that part of OTel has no value. There are mainly 4 things that are hard to get without runtime instrumentation.

- **Exact causal structure** — which operation called which. Only IDs issued at execution time capture this precisely
- **Context propagation across services** — the machinery that stitches one trace across multiple services
- **Real-time visibility** — latency and errors happening right now, visible as they happen
- **Metrics** — numbers aggregated continuously while running. You can technically produce them from an after-the-fact conversion too, but they're fundamentally a signal meant to be measured live

Of these, the last 3 have no reader in my operation — a single process, with nobody watching continuously. The only one genuinely missing is the first, and its minimal patch is row 2 of the table, the "run-ID machinery."

The sections below implement the ✅ elements in order.

## My logs mapped almost 1:1 onto the standard vocabulary

My homegrown telemetry writes one line per LLM call. A line looks like this (simplified):

```json
{"ts": "2026-07-15T09:12:03+09:00", "model": "gemma4:e4b", "prompt_eval_count": 1560, "eval_count": 210, "duration_ms": 36400, "done_reason": "stop"}
```

The next table matches these fields against the GenAI semantic conventions attribute names (the naming table for how to record model name, token counts, finish reason, and so on in OTel).

| My log field | OTel attribute |
|---|---|
| `model` | `gen_ai.request.model` |
| `prompt_eval_count` (input token count) | `gen_ai.usage.input_tokens` |
| `eval_count` (output token count) | `gen_ai.usage.output_tokens` |
| `done_reason` (`stop` / `length`) | `gen_ai.response.finish_reasons` (array-typed, so wrap as `[done_reason]`) |
| `num_predict` (generation cap) | `gen_ai.request.max_tokens` |
| `temperature` | `gen_ai.request.temperature` |
| `error_kind` (`timeout` / `http_429` etc.) | `error.type` |
| `ts` + `duration_ms` | start / end time of the span (one interval of a trace) |
| `caller` (which processing stage made the call), `prompt_sha256`, etc. | No counterpart → custom namespace `ca.audit.*` |

It mapped almost 1:1. For a simple LLM call log like this one (model, token counts, stop reason, parameters), I suspect the set of things you'd want to record converges to the same collection no matter who designs it (logs that also cover tool calls, streaming, or routing won't map this cleanly).

This is where riding the standard vocabulary pays off. If the attribute name is `gen_ai.usage.input_tokens`, external tools and people alike can read it with no explanation.

The interesting part is **what didn't map**. `caller` (the key I use to aggregate logs by processing stage during incident investigation) and `prompt_sha256` (a hash for matching identical prompts without storing the body) have no standard counterpart. These two are investigation keys specific to my operation. For just looking around in a UI, the standard attributes are mostly enough; for offline reproduction of an incident, these are the ones that matter.

:::details Practical handling of the Development status (official status name: Development)
The GenAI semantic conventions (semconv below) are in Development status as of this writing (2026-07) ([canonical repository](https://github.com/open-telemetry/semantic-conventions-genai)). The `opentelemetry-semantic-conventions` package does have attribute-name constants, but they live under an underscore-prefixed (= unstable) `_incubating` import path.

The conversion script doesn't import from the package. Instead, **the attribute names are defined as string constants in my own code, with the referenced semconv version pinned in a comment**. If the standard moves, catching up is a single-file change.
:::

## The conversion script has exactly 3 design points

Let's pin down spans properly here. At the top I described a trace as "a collection of timestamped intervals." Each of those intervals is a span: it has a name, start and end times, and attributes (key-value pairs), and spans connect through parent-child links into one trace. In a Jaeger waterfall, one row is one span.

So the core of the conversion is "read JSONL, create spans with past timestamps." There were 3 design decisions.

### 1. Spans can be created at past timestamps

The OTel SDK lets you explicitly set a span's start and end times in epoch nanoseconds. I restore them directly from the log's `ts` and `duration_ms`.

```python:emit.py (excerpt, simplified)
# Create the span at the log's recorded time (the core of the conversion script)
span = tracer.start_span(
    name,                      # e.g. "text_completion gemma4:e4b"
    context=parent_ctx,
    kind=kind,                 # SpanKind (CLIENT etc. for LLM calls)
    attributes=attrs,
    start_time=start_ns,       # ts converted to epoch ns
)
if is_error:
    span.set_status(Status(StatusCode.ERROR, error_type))
span.end(end_time=end_ns)      # start_ns + duration_ms
```

For logs that don't record a duration (API audit, solver audit), I made the spans **zero-width**. Giving them a plausible width by estimation would mean fabricating latency that was never measured. Jaeger draws zero-width spans as thin markers, so they're also visually distinct from the LLM spans that carry real durations. The fact that "logs without a duration become zero-width" was itself feedback into the log schema (it pinpointed the next improvement candidate: add elapsed time to the API audit log too).

### 2. Trace grouping is reconstructed from gaps in time

A trace is normally bundled by IDs issued at execution time. Past logs don't have those. So I merge the 3 log kinds in timestamp order and **start a new trace whenever a gap of a fixed length (default 300 seconds) opens up**. A schedule-launched agent repeats "a few minutes of activity → long silence," so this cut lines up well with an actual single run. Conversely, for workloads where the logs never pause — parallel runs, always-on workers — this cut will merge things incorrectly.

But it is still an estimate. I put a `ca.convert.grouping = "time-gap"` attribute on each trace's root span, making **the data itself say it is a reconstruction, not a measurement**.

Flip that around and this was **a gap in my own log design that only became visible against OTel**: add one field to every log line — a per-run ID (the equivalent of OTel's trace ID) — and this reconstruction turns from estimation into measurement.

Even if you never adopt the SDK, the one mechanism worth borrowing up front is "stamp every run with an ID."

I implemented it in my agent while writing this article: a single write function shared by all audit logs now stamps `run_id` (per process) and `session_id` (per agent session). That is the only agent-side change in this whole effort, and converting past logs still works with the agent untouched. The converter bundles by ID when `run_id` exists and falls back to time gaps only for older logs. If you're designing logs now, I recommend putting it in from day one.

### 3. Untrusted text is dropped at the conversion entrance

The third design decision is the boundary of what gets onto the Jaeger screen.

The audit log contains raw text that came from outside (CAPTCHA challenge texts, server error response bodies), stored as base64. As described at the top, this agent's input comes from a social network where prompt injection is routine — "strings from outside may be attack input" is the default assumption. Put such text into span attributes, and **attacker-controlled strings flow straight onto the Jaeger screen (= into screenshots, = into this article)**.

The conversion drops bodies at the parser stage and passes through only a sha256 hash and a classification code (`http_400` etc.). There is no "flag to include bodies" either. On top of that, I added a regression test that scans every attribute value of every test fixture and asserts that no body fragment appears. Not "be careful later," but "make it structurally unable to appear, then visualize" — that's the safe side.

To be clear, the goal here is not to keep bodies secret but to avoid carrying external strings onto the screen. The sha256 is a correlation identifier for matching identical inputs, not an anonymization mechanism (short boilerplate strings can be brute-forced back). If your logs hold confidential data, consider a keyed hash (HMAC) or simply not surfacing the hash at all.

## Looking at it in Jaeger — the incident day was obvious the moment I opened it

Jaeger v2 is a single binary; once started, it accepts OTLP directly and keeps everything in memory. Because it takes OTLP directly, there's no need for the Collector I called "heavy" at the top, either.

```bash
# Start the viewer (no Docker; data disappears when it exits)
# For Apple Silicon. On Intel Macs read darwin-amd64; on Linux, linux-amd64
curl -sLO https://github.com/jaegertracing/jaeger/releases/download/v2.19.0/jaeger-2.19.0-darwin-arm64.tar.gz
tar xzf jaeger-2.19.0-darwin-arm64.tar.gz
./jaeger-2.19.0-darwin-arm64/jaeger    # OTLP :4318 / UI :16686

# Convert and send (example run; see the repository README for setup)
contemplative-agent-otel --date 2026-07-15
# => emitted 1031 spans across 5 runs -> http://localhost:4318
```

A normal day looks like this. Reading the screen: time runs along the horizontal axis, one row is one span, parent-child structure is indentation, errors are red marks. One trace is one agent run, with LLM calls carrying real durations (`text_completion gemma4:e4b`, 36 seconds or 1.3 minutes) and zero-width API calls lined up in time order.

![Trace of a normal day: under the agent run root span, LLM calls and API calls lined up in time order as a waterfall](/images/agent-logs-to-opentelemetry-waterfall.png)

Open a span and the mapping table from earlier appears directly as attributes. Standard attributes like `gen_ai.usage.input_tokens: 1560` sit alongside custom ones like `ca.audit.caller: core.skill_selection`.

![Span detail: gen_ai.* standard attributes and ca.audit.* custom attributes side by side](/images/agent-logs-to-opentelemetry-span-genai.png)

And here's what converting the day with the incident produces. On that day, a retry storm (failed calls whose retries cascade until calls and logs balloon) had in fact hit the LLM backend.

![Search results for the incident day: a trace with 30442 spans / 33 errors sits at the top](/images/agent-logs-to-opentelemetry-incident.png)

Where a normal run has tens to hundreds of spans, **one trace with 30,442 spans and 33 errors** towers over everything. The log file for that day was also nearly 30 times its normal size. As numbers, this information was already in the logs — but "you know it's an abnormal day the moment you open it" is a strength unique to trace visualization.

You can follow the errors too. In the run where the CAPTCHA answer was rejected by the server, `captcha solve` and `POST /verify` are marked red as a pair. The error bodies were dropped by the conversion, so all the screen shows is the classification: `error.type: http_400`.

![A run containing errors: red error marks on captcha solve and POST /verify](/images/agent-logs-to-opentelemetry-error-run.png)

:::details Gotcha: send 30,442 spans at once and they're silently dropped
In the OTel SDK, `span.end()` doesn't send immediately — a `BatchSpanProcessor` (an SDK-internal component that queues spans and sends them in batches) does the exporting. In the incident-day conversion, spans beyond the default queue length of 2048 were **discarded with only a one-line warning** (`Queue full, dropping Span.`). For real-time instrumentation that's a reasonable self-defense; for an offline bulk conversion, "send everything" is the correct spec.

Since the number of records to convert is known before sending, I sized the queue to the record count and that solved it. If you use the SDK for bulk conversion, watch out: the defaults assume real time.
:::

## Summary

- Instead of a binary "adopt OTel or don't," I tried the third option: **after-the-fact conversion of existing logs**. Zero changes to the agent, two dependencies — and you get the Jaeger waterfall, error display, and standard attributes, all of it
- My homegrown LLM call log mapped **almost 1:1** onto the GenAI semantic conventions. The fields that didn't map remain as a list of "information needed for offline reproduction of incidents"
- Traces serve humans investigating on a screen (bodies unrecorded by default); the audit log serves machines re-executing for incident reproduction (bodies stored in full). **Different consumers flip the retention policy**, so in a conversion, dropping untrusted bodies at the entrance is the safe side
- Master 3 things — span creation at past timestamps, zero-width spans, trace reconstruction from time gaps — and any structured log from which times and run groupings can be recovered connects the same way
- Add one run-ID field to your logs and the reconstruction itself becomes unnecessary. Even without the SDK, this one mechanism is worth borrowing from OTel up front (I implemented it while writing this article)
- This conversion was also **a way to measure my own log design against OTel as a yardstick**. The missing run ID and the real-time assumptions of the export queue both became visible only against the standard

## Related links

- [contemplative-agent-otel](https://github.com/shimo4228/contemplative-agent-otel) — this article's conversion script (mapping table and tests included)
- [ADR-0078: OTel Connection via Vocabulary Mapping and Offline Export](https://github.com/shimo4228/contemplative-agent/blob/main/docs/adr/0078-otel-connection-via-vocabulary-and-offline-export.md) — the primary source for this decision ([ADR-0075](https://github.com/shimo4228/contemplative-agent/blob/main/docs/adr/0075-observability-by-default.md): the companion decision to ship audit logs in the same PR as the feature)
- [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai) — canonical source of the standard vocabulary (Development status)
- [Previous article: Why Did My Agent Decide That? 3 Observability Patterns](https://dev.to/shimo4228/why-did-my-agent-decide-that-3-observability-patterns-ami) — the 3 design patterns on the audit-log side
- [Can You Trace the Cause After an Incident?](https://dev.to/shimo4228/can-you-trace-the-cause-after-an-incident-neo) — one step further back: why records that let you trace causality after an agent incident matter in the first place
- [Building an Autonomous Agent on an M1 Mac — by Choice](https://dev.to/shimo4228/building-an-autonomous-agent-on-an-m1-mac-by-choice-5b5o) — hub of the small-LLM series this article belongs to
- [My GitHub](https://github.com/shimo4228) — the agent itself and related repositories
