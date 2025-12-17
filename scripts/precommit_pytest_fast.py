"""Utility for the pre-commit hook that runs the fast pytest subset."""

from __future__ import annotations

import os
import subprocess
import sys


def main() -> int:
    env = os.environ.copy()
    env.setdefault("SIFU_SKIP_BOOTSTRAP", "1")

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "tests/test_api_simple.py",
        "tests/test_ur_api.py::TestUREndpoints::test_get_latest_ur_success",
    ]

    result = subprocess.run(cmd, env=env)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
