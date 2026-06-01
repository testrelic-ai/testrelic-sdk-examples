"""Offline end-to-end verification — proves the demo captures and uploads the
full metric set WITHOUT touching the real cloud or needing an API key.

Sequence:
  1. start the dependency-free mock server (runs + evals) on 127.0.0.1:8799
  2. run `pytest tests/` against it with a `tr_` test key (upload=both)
  3. (if deepeval is installed) run `pytest evals/` against it
  4. read received_runs.jsonl / received_evals.jsonl and assert:
       - the batch POST /runs arrived with a Bearer tr_ token
       - run summary + per-test phases are present
       - the protocol surface is captured: apiProtocol, streamingMetadata,
         protocolAssertions, apiCalls all appear across the run
       - evals (when run) follow POST /runs -> PUT cases -> POST finalize
  5. print a PASS/FAIL report + a sample payload.

Usage:  python verification/verify.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
PORT = 8799
BASE = f"http://127.0.0.1:{PORT}"
RECEIVED_RUNS = HERE / "received_runs.jsonl"
RECEIVED_EVALS = HERE / "received_evals.jsonl"


def _wait_health(timeout: float = 10.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{BASE}/api/v1/health", timeout=1) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.2)
    return False


def _start_mock() -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, str(HERE / "mock_runs_server.py"), str(PORT)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def _run_pytest(target: str, env: dict, extra: tuple = ()) -> int:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", target, "-q", "-p", "no:cacheprovider", *extra],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )
    print(f"\n--- pytest {target} (exit {proc.returncode}) ---")
    print(proc.stdout[-3000:])
    if proc.returncode not in (0, 1):  # 1 = some tests failed (expected in chaos runs)
        print(proc.stderr[-2000:])
    return proc.returncode


def _records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def main() -> int:
    for f in (RECEIVED_RUNS, RECEIVED_EVALS):
        f.unlink(missing_ok=True)

    env = os.environ.copy()
    env["TESTRELIC_API_KEY"] = "tr_verification_demo_key"
    env["TESTRELIC_CLOUD_ENDPOINT"] = f"{BASE}/api/v1"
    env["TESTRELIC_BASE_URL"] = f"{BASE}/api/v1/evals"
    env["TESTRELIC_UPLOAD_STRATEGY"] = "both"
    env["TESTRELIC_PROJECT_NAME"] = "shoprelic-pytest-demo"
    env["TESTRELIC_QUIET"] = "0"
    env["DEEPEVAL_TELEMETRY_OPT_OUT"] = "1"
    env.pop("CONFIDENT_API_KEY", None)

    print(f"[1] starting mock server on {BASE} ...")
    server = _start_mock()
    try:
        if not _wait_health():
            out, err = server.communicate(timeout=2)
            print("MOCK STDOUT:", out.decode(errors="replace"))
            print("MOCK STDERR:", err.decode(errors="replace"))
            return 2
        print("    health OK")

        print("[2] running protocol suite (tests/) ...")
        _run_pytest("tests", env)

        have_deepeval = subprocess.run(
            [sys.executable, "-c", "import deepeval"], capture_output=True
        ).returncode == 0
        if have_deepeval:
            print("[3] running eval suite (evals/) ...")
            # Disable the generic reporter so the eval tests upload only as a
            # DeepEval eval run (not also as a duplicate generic pytest run).
            _run_pytest("evals", env, extra=("-p", "no:testrelic_pytest"))
        else:
            print("[3] deepeval not installed — skipping eval verification")

        time.sleep(1.0)  # let fire-and-forget realtime uploads flush
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

    print("\n[4] validating wire payloads ...")
    runs = _records(RECEIVED_RUNS)
    evals = _records(RECEIVED_EVALS)
    issues: list[str] = []

    batch = next((r for r in runs if r["path"].endswith("/runs")), None)
    if batch is None:
        issues.append("no batch POST /runs received")
    else:
        # The SDK exchanges the tr_ key for an access token, so /runs carries the
        # *exchanged* bearer token (not the raw tr_ key — that only goes to
        # /sdk/auth/token).
        if not batch["headers"].get("authorization", "").lower().startswith("bearer "):
            issues.append("batch /runs missing Bearer token")
        body = batch["body"]
        for field in ("runId", "repoGitId", "testFramework", "startedAt", "summary", "tests"):
            if field not in body:
                issues.append(f"run payload missing {field}")
        summary = body.get("summary", {})
        for k in ("total", "passed", "failed", "skipped", "xfailed", "xpassed"):
            if k not in summary:
                issues.append(f"summary missing {k}")
        tests = body.get("tests", [])
        if not any(t.get("phases") for t in tests):
            issues.append("no test carried phases[]")
        if not any(t.get("apiProtocol") for t in tests):
            issues.append("no test carried apiProtocol (auto-detect/fixtures not capturing)")
        if not any(t.get("streamingMetadata") for t in tests):
            issues.append("no test carried streamingMetadata (kafka/ws/grpc)")
        if not any(t.get("protocolAssertions") for t in tests):
            issues.append("no test carried protocolAssertions")
        if not any(t.get("apiCalls") for t in tests):
            issues.append("no test carried apiCalls (rest/graphql/mcp)")

    if have_deepeval and not evals:
        issues.append("deepeval installed but no eval upload reached /api/v1/evals")
    if evals:
        seq = [(r["method"], r["path"].split("/evals/")[-1]) for r in evals]
        if not any(m == "POST" and p == "runs" for m, p in seq):
            issues.append("evals: no create POST /evals/runs")
        if not any(m == "PUT" and p.endswith("/cases") for m, p in seq):
            issues.append("evals: no PUT cases")
        if not any(m == "POST" and p.endswith("/finalize") for m, p in seq):
            issues.append("evals: no POST finalize")
        all_cases = [c for r in evals if r["method"] == "PUT" for c in r["body"].get("cases", [])]
        if not all_cases:
            issues.append("evals: no cases uploaded")
        if not any(c.get("metrics") for c in all_cases):
            issues.append("evals: no metric scores uploaded")

    print("=" * 64)
    print("VERIFICATION REPORT")
    print("=" * 64)
    print(f"runs requests:    {len(runs)} (batch: {'yes' if batch else 'no'})")
    print(f"evals requests:   {len(evals)}")
    if batch:
        protos = sorted({t.get("apiProtocol") for t in batch['body'].get('tests', []) if t.get('apiProtocol')})
        print(f"protocols seen:   {protos}")
        print(f"summary:          {batch['body'].get('summary')}")
    print(f"contract issues:  {len(issues)}")
    for s in issues:
        print(f"  - {s}")

    if batch:
        sample = next((t for t in batch["body"]["tests"] if t.get("streamingMetadata")), None)
        if sample:
            print("\nSample streaming test payload:")
            print(json.dumps(sample, indent=2)[:1800])

    ok = not issues and batch is not None
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
