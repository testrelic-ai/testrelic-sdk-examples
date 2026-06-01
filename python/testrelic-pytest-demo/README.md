# TestRelic pytest demo — ShopRelic API

A fully-working sample repo that showcases the **TestRelic Python SDK suite** end to
end and uploads real runs to the TestRelic cloud:

- **`testrelic-pytest`** across **every API protocol** it supports — REST, GraphQL,
  gRPC, WebSocket, Kafka, MCP — plus plain pytest (units, parametrize, xfail, flaky).
- **`testrelic-deepeval`** — hermetic LLM-evaluation runs (deterministic, no API key).
- **`testrelic-playwright`** — a small browser suite.
- **`testrelic-appium`** — a mobile suite that auto-skips without a device.

It ships a real **FastAPI app** ("ShopRelic API") so REST/GraphQL are exercised over
live HTTP, and an offline **mock server + `verify.py`** so you can prove the full
metric payload without a key or network.

## What gets captured (the "all metrics" checklist)

Per test: status, duration, per-phase timings (setup/call/teardown), markers,
keywords, parametrize ids, warnings, failure tracebacks + assertion repr, captured
stdout/stderr/log, flaky/retry. Per protocol test: `apiProtocol`,
`streamingMetadata` (topics/partitions/offsets/consumer-lag), `protocolAssertions`,
and `apiCalls` (request/response inspector). Per run: summary
(total/passed/failed/skipped/xfailed/xpassed), CI + git branch/commit, run-type
bucket. DeepEval runs add test cases + metric scores/thresholds.

## Quick start

```bash
python -m venv .venv && .venv\Scripts\activate      # (PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt
```

> **Install note.** The SDKs install straight from PyPI — no monorepo checkout
> needed. The demo pins `testrelic-pytest >= 0.3` because the protocol fixtures +
> HTTP auto-detection require it.

### 1. Prove it works offline (no key, no network)

```bash
python verification/verify.py
```
Starts a local mock cloud, runs the protocol suite against it, and asserts that the
uploaded payload contains every required metric field. Prints `RESULT: PASS`.

### 2. Run against the real cloud

```bash
set TESTRELIC_API_KEY=tr_live_...        # PowerShell: $env:TESTRELIC_API_KEY="tr_live_..."
pytest tests/
```
You'll see `testrelic: uploaded N test result(s) to TestRelic cloud`. Add
`--testrelic-pytest-output run.json` to inspect the exact payload locally.

### 3. Seed the regression → recovery story (15 runs)

```bash
python seed_runs.py            # real cloud (needs TESTRELIC_API_KEY)
python seed_runs.py --mock     # dry run against the local mock
```
Produces a pass-rate arc (~95% → ~65% → ~95%): a checkout regression at run 8
(`v1.3.0`), a flaky search in runs 10–13, a profile regression at run 12, and full
recovery at run 14 — while the streaming protocols stay green throughout.

### 4. The other SDKs

```bash
pip install -r requirements-evals.txt && pytest evals/ -p no:testrelic_pytest   # DeepEval (hermetic)
playwright install chromium && pytest ui/                                       # Playwright
pip install -r requirements-appium.txt && pytest mobile/                        # Appium (skips w/o device)
```

> The eval suite is run with `-p no:testrelic_pytest` so its tests upload only as a
> DeepEval eval run (to `/api/v1/evals`) rather than *also* as a duplicate generic
> pytest run. `verify.py` and `seed_runs.py` add this flag automatically.

## Layout

```
shoprelic_api/        FastAPI app (REST + GraphQL + WS) with env-flag chaos injection
tests/                testrelic-pytest suites — one per protocol + units + e2e
ui/                   testrelic-playwright browser suite
mobile/               testrelic-appium suite (auto-skips without a device)
evals/                testrelic-deepeval suite (deterministic FixedScoreMetric)
verification/         dependency-free mock cloud + verify.py (offline proof)
.testrelic/           cloud config (apiKey via $TESTRELIC_API_KEY)
seed_runs.py          15-run regression→recovery seeder
```

## How protocols are exercised

- **REST / GraphQL** hit the live FastAPI app over `httpx` and are auto-detected (no
  fixture needed). The 4s client timeout vs the 6s `FLAKY_INVENTORY` delay is what
  turns a slow search into a recorded flaky failure.
- **Kafka / gRPC / WebSocket / MCP** use the SDK fixtures in **synthetic/manual mode**
  — realistic `streamingMetadata` + `protocolAssertions` with no brokers, so the demo
  runs anywhere.

## Chaos flags

| Flag | Effect | Tests affected |
|---|---|---|
| `BREAK_PAYMENT` | `POST /api/checkout` → 500 gateway timeout | REST checkout + e2e |
| `BREAK_PROFILE` | profile/orders empty | REST + GraphQL "my orders" |
| `FLAKY_INVENTORY` | search 50% slow → client timeout | REST + GraphQL search |
| (always on) | coupon endpoint returns 0% discount, untested | coverage-gap story |

## Test user

`demo@shoprelic.com` / `password123`
