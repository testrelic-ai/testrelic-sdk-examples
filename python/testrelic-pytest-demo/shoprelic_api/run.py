"""Launch the ShopRelic API with uvicorn, honouring PORT + chaos env vars.

    python -m shoprelic_api.run
    PORT=8000 BREAK_PAYMENT=true python -m shoprelic_api.run
"""

from __future__ import annotations

import os


def main() -> None:
    import uvicorn

    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    # No reload: chaos flags are read at import time, one clean "deploy" per process.
    uvicorn.run("shoprelic_api.main:app", host=host, port=port, log_level="warning")


if __name__ == "__main__":
    main()
