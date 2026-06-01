---
name: verify
description: Prove the demo captures and uploads the full metric set, offline.
---

```bash
python verification/verify.py
```

Starts a dependency-free mock cloud, runs `tests/` (and `evals/` if deepeval is
installed) against it, then asserts the uploaded payload contains the batch
`POST /runs` with a Bearer `tr_` token, the run summary, per-test phases, and the
protocol surface (`apiProtocol`, `streamingMetadata`, `protocolAssertions`,
`apiCalls`). Prints `RESULT: PASS`. No API key or network required.

Inspect the captured payloads at `verification/received_runs.jsonl` and
`verification/received_evals.jsonl`.
