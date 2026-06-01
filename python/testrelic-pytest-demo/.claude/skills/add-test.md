---
name: add-test
description: How to add a new protocol or plain test to the suite.
---

- **REST/GraphQL (real HTTP):** add a test under `tests/` that uses the `client`
  fixture (httpx). No TestRelic code needed — httpx calls are auto-captured as `rest`.
- **Streaming/synthetic protocol:** request the fixture by name and drive it in manual
  mode — `testrelic_kafka`, `testrelic_grpc`, `testrelic_ws`, `testrelic_mcp`,
  `testrelic_graphql`. See `tests/test_kafka_streaming.py` for the method set
  (produce/consume/assert_*).
- **Plain pytest:** import from `shoprelic_api.data`; use markers from `pyproject.toml`.
- Mark tests with `@pytest.mark.{smoke,regression,api,streaming,nightly}` so they bucket
  correctly in the dashboard.
- Tie a new failure to the story by reading a chaos flag in `shoprelic_api/chaos.py`.
