---
name: run-tests
description: Run the testrelic-pytest protocol suites (and the other SDK suites).
---

Protocol + unit suite (needs a real key to upload, or use the verify skill offline):
```bash
pytest tests/
pytest tests/ --testrelic-pytest-output run.json   # also dump the payload locally
pytest tests/test_kafka_streaming.py -v            # a single protocol
```

Other SDKs (separate invocations — the plugins are distinct):
```bash
pip install -r requirements-evals.txt && pytest evals/ -p no:testrelic_pytest
playwright install chromium && pytest ui/
pytest mobile/        # auto-skips without an Appium device
```
The eval suite uses `-p no:testrelic_pytest` so its tests upload only as a DeepEval
eval run, not also as a duplicate generic pytest run.

Upload only happens when `TESTRELIC_API_KEY` (a `tr_` key) is set.
