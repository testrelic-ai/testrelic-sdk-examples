---
name: seed-demo
description: Seed the 15-run regression→recovery story for the dashboard.
---

```bash
python seed_runs.py            # real cloud (export TESTRELIC_API_KEY first)
python seed_runs.py --mock     # dry run against the local mock server
```

Produces the arc: ~95% baseline (runs 1–7) → checkout regression at run 8 (`v1.3.0`)
→ flaky search (runs 10–13) → profile regression (run 12) → full recovery at run 14
(`v1.5.0`). Nightly rows (3, 7, 11, 14) also run the eval + Playwright suites when
those optional deps are installed.
