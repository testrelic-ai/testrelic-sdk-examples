"""Seed a regression -> recovery story across ~15 runs (cross-platform).

Each run = one "deploy": chaos flags + commit/build/deploy metadata are set in the
environment, then `pytest tests/` runs (the app boots in-process per run, reading
that run's chaos flags). Nightly rows also run the eval + Playwright suites when
those optional deps are installed.

Real cloud:   set TESTRELIC_API_KEY, then:  python seed_runs.py
Dry run:      python seed_runs.py --mock        (uploads to a local mock server)

The pass-rate arc:  ~95% -> ~70% (checkout) -> ~65% (+flaky) -> ~80% (profile) -> ~95%.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

# run, runType, BREAK_PAYMENT, BREAK_PROFILE, FLAKY_INVENTORY, deploy, commit, story
ARC = [
    (1,  "smoke",      False, False, False, "v1.0.0", "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0", "healthy baseline"),
    (2,  "regression", False, False, False, "v1.0.1", "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1", "healthy"),
    (3,  "nightly",    False, False, False, "v1.0.2", "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2", "healthy + evals/ui"),
    (4,  "regression", False, False, False, "v1.1.0", "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3", "healthy"),
    (5,  "smoke",      False, False, False, "v1.1.1", "e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4", "healthy"),
    (6,  "regression", False, False, False, "v1.2.0", "f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5", "healthy"),
    (7,  "nightly",    False, False, False, "v1.2.1", "a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6", "last green + evals/ui"),
    (8,  "regression", True,  False, False, "v1.3.0", "b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7", "checkout deploy BREAKS payment"),
    (9,  "regression", True,  False, False, "v1.3.0", "c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8", "still red"),
    (10, "regression", True,  False, True,  "v1.3.1", "d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9", "+ flaky search"),
    (11, "nightly",    True,  False, True,  "v1.3.1", "e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0", "still red + evals/ui"),
    (12, "regression", False, True,  True,  "v1.4.0", "f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1", "partial fix: profile regresses"),
    (13, "regression", False, True,  True,  "v1.4.0", "a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2", "still profile-red"),
    (14, "nightly",    False, False, False, "v1.5.0", "b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3", "full recovery + evals/ui"),
    (15, "smoke",      False, False, False, "v1.5.0", "c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4", "green confirmation"),
]


def _has(module: str) -> bool:
    return subprocess.run([sys.executable, "-c", f"import {module}"], capture_output=True).returncode == 0


def _pytest(target: str, env: dict, extra: tuple = ()) -> None:
    print(f"    $ pytest {target} {' '.join(extra)}".rstrip())
    subprocess.run(
        [sys.executable, "-m", "pytest", target, "-q", "-p", "no:cacheprovider", *extra],
        env=env, check=False,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true", help="upload to a local mock server instead of prod")
    args = ap.parse_args()

    mock_proc = None
    base_env = os.environ.copy()
    base_env["TESTRELIC_UPLOAD_STRATEGY"] = "both"

    if args.mock:
        from pathlib import Path
        mock = Path(__file__).parent / "verification" / "mock_runs_server.py"
        mock_proc = subprocess.Popen([sys.executable, str(mock), "8799"])
        time.sleep(1.5)
        base_env["TESTRELIC_API_KEY"] = "tr_seed_demo_key"
        base_env["TESTRELIC_CLOUD_ENDPOINT"] = "http://127.0.0.1:8799/api/v1"
        base_env["TESTRELIC_BASE_URL"] = "http://127.0.0.1:8799/api/v1/evals"
    elif not base_env.get("TESTRELIC_API_KEY"):
        print("[!] TESTRELIC_API_KEY is not set. Export a real tr_ key, or use --mock.")
        return 1
    else:
        base_env.setdefault("TESTRELIC_BASE_URL", "https://platform.testrelic.ai/api/v1/evals")

    have_evals = _has("deepeval")
    have_ui = _has("playwright")

    try:
        for run, run_type, brk_pay, brk_prof, flaky, deploy, commit, story in ARC:
            print("\n" + "=" * 60)
            print(f" Run {run}/15  [{run_type}]  deploy={deploy}  commit={commit[:8]}")
            print(f"   BREAK_PAYMENT={brk_pay} BREAK_PROFILE={brk_prof} FLAKY_INVENTORY={flaky}")
            print(f"   story: {story}")
            print("=" * 60)

            env = dict(base_env)
            env["BREAK_PAYMENT"] = "true" if brk_pay else "false"
            env["BREAK_PROFILE"] = "true" if brk_prof else "false"
            env["FLAKY_INVENTORY"] = "true" if flaky else "false"
            env["FLAKY_UNIT"] = "true" if flaky else "false"
            env["TESTRELIC_RUN_TYPE"] = run_type
            env["TESTRELIC_PROJECT_NAME"] = "shoprelic-pytest-demo"
            env["BUILD_NUMBER"] = str(run)
            env["DEPLOY_TAG"] = deploy
            env["COMMIT_SHA"] = commit
            # CI-like signals so the SDK records branch/commit/run-url metadata.
            env["GITHUB_SHA"] = commit
            env["GITHUB_REF_NAME"] = "main"

            _pytest("tests", env)
            if run_type == "nightly":
                if have_evals:
                    # Disable the generic reporter so eval tests upload only as a
                    # DeepEval eval run (not also as a duplicate generic run).
                    _pytest("evals", env, extra=("-p", "no:testrelic_pytest"))
                if have_ui:
                    _pytest("ui", env)
            time.sleep(0.5)
    finally:
        if mock_proc is not None:
            mock_proc.terminate()

    print("\nSeed complete. Open the TestRelic dashboard for the shoprelic-pytest-demo project:")
    print("  - pass-rate trend ~95% -> ~65% -> ~95%")
    print("  - regression at run 8 (v1.3.0), MTTR through run 14 (v1.5.0)")
    print("  - flaky search in runs 10-13; streaming protocols stay green throughout")
    return 0


if __name__ == "__main__":
    sys.exit(main())
