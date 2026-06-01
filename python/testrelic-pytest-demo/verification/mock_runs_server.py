"""Dependency-free mock of the TestRelic cloud for offline verification.

Serves BOTH contracts from a single stdlib server (no FastAPI), so one process
backs every SDK in the demo. Point both env vars at it:

    TESTRELIC_CLOUD_ENDPOINT = http://127.0.0.1:8799/api/v1          (pytest / playwright)
    TESTRELIC_BASE_URL       = http://127.0.0.1:8799/api/v1/evals    (deepeval)

Runs contract (testrelic-pytest / -playwright):
  GET  /api/v1/health
  POST /api/v1/sdk/auth/token | /sdk/auth/refresh   -> JWT bundle
  POST /api/v1/repos/resolve                        -> { repoId, displayName }
  POST /api/v1/runs                                 -> batch          (recorded)
  POST /api/v1/runs/init                            -> { runId }      (recorded)
  POST /api/v1/runs/{id}/tests                      -> per-test       (recorded)
  POST /api/v1/runs/{id}/finalize                   -> { }            (recorded)

Evals contract (testrelic-deepeval):
  POST /api/v1/evals/runs                           -> { data:{evalRunId} }   (recorded)
  PUT  /api/v1/evals/runs/{id}/cases               -> { data:{...} }          (recorded)
  POST /api/v1/evals/runs/{id}/finalize            -> { data:{finalized} }    (recorded)

Run records -> received_runs.jsonl, eval records -> received_evals.jsonl.
Usage: python verification/mock_runs_server.py [port]   (default 8799)
"""

from __future__ import annotations

import gzip
import json
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).parent
RECEIVED_RUNS = HERE / "received_runs.jsonl"
RECEIVED_EVALS = HERE / "received_evals.jsonl"
RECEIVED_RUNS.unlink(missing_ok=True)
RECEIVED_EVALS.unlink(missing_ok=True)

TOKEN_BUNDLE = {
    "accessToken": "acc_mock_token",
    "refreshToken": "ref_mock_token",
    "expiresIn": 3600,
    "orgId": "org-mock",
    "orgName": "Mock Org",
    "userId": "user-mock",
    "userName": "Mock User",
}


def _append(path_file: Path, method: str, path: str, headers: dict, body: object) -> None:
    with path_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(
            {"method": method, "path": path,
             "headers": {k.lower(): v for k, v in headers.items()}, "body": body},
            default=str,
        ) + "\n")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # silence stderr noise
        pass

    def _send(self, code: int, payload: object) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_body(self) -> object:
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b""
        if self.headers.get("Content-Encoding") == "gzip" and raw:
            raw = gzip.decompress(raw)
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except ValueError:
            return {"_raw": raw.decode("utf-8", "ignore")}

    # ── shared ────────────────────────────────────────────────────────────
    def do_GET(self):
        if self.path.endswith("/health"):
            return self._send(200, {"status": "ok"})
        return self._send(404, {"error": {"code": "NOT_FOUND", "message": self.path}})

    def do_PUT(self):
        path, body = self.path, self._read_body()
        if "/evals/runs/" in path and path.endswith("/cases"):
            _append(RECEIVED_EVALS, "PUT", path, dict(self.headers), body)
            cases = body.get("cases", []) if isinstance(body, dict) else []
            metrics = sum(len(c.get("metrics", [])) for c in cases)
            return self._send(200, {"data": {"insertedCases": len(cases), "insertedMetrics": metrics}})
        return self._send(404, {"error": {"code": "NOT_FOUND", "message": path}})

    def do_POST(self):
        path, body = self.path, self._read_body()

        # auth + repo resolve (shared by both contracts)
        if path.endswith("/sdk/auth/token") or path.endswith("/sdk/auth/refresh"):
            return self._send(200, TOKEN_BUNDLE)
        if path.endswith("/repos/resolve"):
            return self._send(200, {"repoId": "repo-mock-1", "displayName": "shoprelic-api"})

        # evals contract
        if "/evals/runs" in path:
            _append(RECEIVED_EVALS, "POST", path, dict(self.headers), body)
            if path.endswith("/finalize"):
                return self._send(200, {"data": {"finalized": True}})
            return self._send(201, {"data": {"evalRunId": str(uuid.uuid4())}})

        # runs contract
        if path.endswith("/runs/init"):
            run_id = (body or {}).get("runId", "run-mock") if isinstance(body, dict) else "run-mock"
            _append(RECEIVED_RUNS, "POST", path, dict(self.headers), body)
            return self._send(200, {"runId": run_id})
        if "/runs" in path:  # /runs (batch), /runs/{id}/tests, /runs/{id}/finalize
            _append(RECEIVED_RUNS, "POST", path, dict(self.headers), body)
            return self._send(200, {"ok": True})

        return self._send(404, {"error": {"code": "NOT_FOUND", "message": path}})


if __name__ == "__main__":
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8799
    print(f"mock-server listening on http://127.0.0.1:{port} (runs + evals)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
