# TestRelic pytest demo — recording flow

**Length:** 3–4 min. **Setup:** seed runs uploaded, dashboard loaded, Cursor + MCP connected.

## Pre-recording checklist
- [ ] `pip install -r requirements.txt` done; `python verification/verify.py` prints PASS
- [ ] `TESTRELIC_API_KEY` exported; `python seed_runs.py` completed (15 runs visible)
- [ ] Dashboard open on the `shoprelic-pytest-demo` project (API workspace)
- [ ] Cursor open with the TestRelic MCP server connected

## Scene 1 — One-line install, all protocols (0:00–0:30)
- Show `requirements.txt` and `.testrelic/testrelic-config.json` (apiKey via env).
- `pytest tests/` → terminal shows the banner: *uploaded N test result(s) to TestRelic cloud*.
- Message: "One pytest plugin captures REST, GraphQL, gRPC, WebSocket, Kafka, and MCP —
  HTTP is auto-detected, streaming protocols via fixtures. Zero code in the tests."

## Scene 2 — Cloud API workspace (0:30–1:15)
- The run auto-routes to the **API workspace** (tests carry `apiProtocol`).
- Trend line across the 15 seeded runs: stable ~95% → drop at run 8 (`v1.3.0`) → recovery at run 14.
- Point out the protocol breakdown: REST/GraphQL went red; Kafka/gRPC/WebSocket/MCP stayed green.

## Scene 3 — Session workspace (1:15–1:45)
- Open a failed `test_checkout_places_order` → **Request/Response inspector**:
  `POST /api/checkout 500 "Payment processing failed: Gateway timeout"`; Assertions tab
  shows `resp.status_code == 201` failing.
- Switch to a Kafka test in the same run → **Streaming panel**: topics, partitions,
  offsets, consumer-lag = 0, ordering assertion passed.

## Scene 4 — Ask AI (1:45–3:00)
Use the prompts in `demo-prompts.md`:
1. "Which API tests broke after the checkout deploy v1.3.0, and on which protocol?"
2. "Did the profile regression affect both REST and GraphQL?"
3. "Compare the streaming surface vs the HTTP surface across the regression."
4. "Generate a sprint review deck with pass-rate trend, top API failures by protocol, and MTTR."
5. "Create a Jira ticket for the checkout payment regression with request/response evidence."

## Scene 5 — MCP in the IDE (3:00–3:40)
- `tr_diagnose_run --run=8`, `tr_ai_rca --test="tests/test_rest_api.py::test_checkout_places_order"`,
  `tr_flaky_audit`, `tr_coverage_gaps` (surfaces the untested coupon endpoint).

## Scene 6 — Wrap (3:40–4:00)
- Show run 14 green; the DeepEval evals dashboard (`/evals`) with the deterministic
  scores; the appium suite reported as skipped (no device). Close on the trend recovering.
