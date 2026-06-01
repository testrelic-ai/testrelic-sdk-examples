---
name: start-app
description: Start the ShopRelic API locally, optionally with chaos flags.
---

Run the FastAPI app:

```bash
python -m shoprelic_api.run
# with chaos:
BREAK_PAYMENT=true FLAKY_INVENTORY=true python -m shoprelic_api.run
```

Defaults to http://127.0.0.1:8000. Health check: `GET /api/health` (also reports the
active chaos flags). Note: the test suites start the app in-process automatically, so
this is only needed for manual exploration or to drive a separate process.
