# TestRelic pytest demo — Ask-AI & MCP prompts

Curated for the API-protocol regression story (15 seeded runs).

## Ask AI (cloud dashboard)

### Regression & protocols
1. **"Which API tests broke after the checkout deploy (v1.3.0), and on which protocol?"**
   → REST `POST /api/checkout` 500s starting run 8 (`test_checkout_places_order`, `test_full_purchase_flow`).
2. **"Did the profile regression affect both REST and GraphQL?"**
   → Yes — `test_profile_shows_order_history` (REST) and `test_graphql_my_orders` (GraphQL) under BREAK_PROFILE (runs 12–13).
3. **"Compare the streaming surface (Kafka/gRPC/WebSocket/MCP) health vs the HTTP surface across the regression."**
   → Streaming stayed green; HTTP (REST/GraphQL) carried every failure.
4. **"What's the root cause of the checkout failures?"**
   → 500 "Payment processing failed: Gateway timeout" from `/api/checkout`; request/response captured.

### Flaky & coverage
5. **"Show me the flaky API tests and their flakiness rate over time."**
   → `test_search_products` + `test_graphql_search` flake in runs 10–13 (FLAKY_INVENTORY).
6. **"Is the coupon endpoint covered by any test?"**
   → Coverage gap: `POST /api/coupons/apply` returns a 0% discount and no test exercises it.

### Reports & integrations
7. **"Generate a sprint review deck with pass-rate trend, top API failures by protocol, and MTTR."**
   → Trend ~95%→~65%→~95%; MTTR run 8 → run 14.
8. **"Create a Jira ticket for the checkout payment regression with request/response evidence."**
9. **"Generate a regression report comparing run 7 (last green) vs run 8 (first red)."**

## MCP commands (Cursor / Claude Desktop)
```
tr_health
tr_list_repos
tr_recent_runs --status=failed
tr_diagnose_run --run=8
tr_ai_rca --test="tests/test_rest_api.py::test_checkout_places_order"
tr_flaky_audit
tr_compare_runs --from=7 --to=8
tr_coverage_gaps
tr_create_jira --test="tests/test_rest_api.py::test_checkout_places_order" --priority=high
```
