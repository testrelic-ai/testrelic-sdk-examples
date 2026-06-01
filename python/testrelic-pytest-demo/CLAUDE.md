# TestRelic pytest demo — project guide

## Overview
ShopRelic API is the **Python/API** demo for the TestRelic SDK suite — the backend
analog of the JS `testrelic-demo` storefront. It exercises **`testrelic-pytest`
across every protocol** (REST, GraphQL, gRPC, WebSocket, Kafka, MCP) plus
`testrelic-deepeval`, `testrelic-playwright`, and `testrelic-appium`, and uploads
real runs to the TestRelic cloud. A regression→recovery seed arc populates the
dashboard with trends, flaky detection, and MTTR.

## Repository structure
```
shoprelic_api/   FastAPI app: main.py (REST), graphql_schema.py, data.py, chaos.py, run.py
tests/           protocol suites (test_rest_api, test_graphql_api, test_kafka_streaming,
                 test_grpc_streaming, test_websocket, test_mcp_tools, test_unit_pricing,
                 test_e2e_order_flow)
ui/              testrelic-playwright browser suite
mobile/          testrelic-appium suite (auto-skips without a device)
evals/           DeepEval suite (metrics.py FixedScoreMetric, test_support_qa_eval.py)
verification/    mock_runs_server.py (stdlib, runs+evals), verify.py (offline proof)
seed_runs.py     15-run regression arc
.testrelic/testrelic-config.json   prod cloud block, apiKey=$TESTRELIC_API_KEY
```

## How it works (key facts)
- **Activation:** the pytest plugin only captures when a `tr_` key resolves AND a
  cloud endpoint or `--testrelic-pytest-output` is set. With no key it silently
  no-ops. Offline mode therefore uses a dummy `tr_` key + the mock endpoint.
- **Two endpoint env vars:** pytest/playwright read `TESTRELIC_CLOUD_ENDPOINT`
  (`…/api/v1`); deepeval reads `TESTRELIC_BASE_URL` (`…/api/v1/evals`). Both share
  `TESTRELIC_API_KEY`. The seed/verify scripts set both.
- **REST/GraphQL** are auto-captured from live `httpx` calls (no fixture). **Kafka/
  gRPC/WebSocket/MCP** use `testrelic_kafka|_grpc|_ws|_mcp` fixtures in manual mode.
- **Run plugins separately:** the four `pytest11` plugins coexist; the seed script
  runs `tests/`, `evals/`, and `ui/` as separate invocations. The eval suite is run
  with `-p no:testrelic_pytest` so its tests upload only as a DeepEval eval run (to
  `/api/v1/evals`), not also as a duplicate generic pytest run. `verify.py` and
  `seed_runs.py` apply this automatically.

## Chaos flags (env vars, read at app start)
- `BREAK_PAYMENT` → checkout 500; `BREAK_PROFILE` → empty order history;
  `FLAKY_INVENTORY` → 50% 6s search delay (client timeout); `FLAKY_UNIT` → flaky unit.
- Coupon endpoint is always bugged (0% discount) and intentionally untested.

## Commands
```bash
pip install -r requirements.txt          # core
python verification/verify.py            # offline proof (no key) — asserts all metrics
pytest tests/                            # real cloud (needs TESTRELIC_API_KEY)
python seed_runs.py [--mock]             # 15-run arc
pip install -r requirements-evals.txt && pytest evals/ -p no:testrelic_pytest   # DeepEval
playwright install chromium && pytest ui/                                       # Playwright
pytest mobile/                                                                  # Appium (auto-skips)
```

## Conventions
- The app boots **in-process** from `tests/conftest.py` (and `ui/conftest.py`) if not
  already reachable at `SHOPRELIC_URL` (default `http://127.0.0.1:8000`), so each
  `pytest` run is self-contained.
- The local `base_url` is exposed as the `app_url` fixture (the name `base_url` is
  reserved by pytest-base-url, which pytest-playwright pulls in).
- Markers are registered in `pyproject.toml` (`smoke/regression/api/streaming/ui/
  appium/flaky/nightly`).
- SDKs install editable from `../testrelic-platform/testrelic-python-sdk` until
  protocols ship to PyPI (`testrelic-pytest >= 0.3`).
- No database — app state is in-memory and resets on restart.

## Test user
`demo@shoprelic.com` / `password123`
