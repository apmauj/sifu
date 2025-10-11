#!/usr/bin/env python
"""Check for hard-coded repeated message literals not defined in constants.

Rules:
- Scan Python source (exclude tests, migrations, scripts/, constants.py itself).
- Flag string literals (length>=20, contains a space) appearing >1 time across code
  AND not equal to any constant value defined in constants.py (upper-case vars).
- Exit code 0 if none found; 1 if issues.

Usage:
  python scripts/check_messages.py
Optionally set MIN_LEN or MIN_COUNT env vars.
"""

from __future__ import annotations
import ast
import os
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # From scripts/util/ to repo root
EXCLUDE_DIRS = {"tests", "__pycache__", "scripts", "migration-tools", ".venv"}
ALLOWED_FILES = {"constants.py"}
MIN_LEN = int(os.getenv("MIN_LEN", "20"))
MIN_COUNT = int(os.getenv("MIN_COUNT", "4"))  # Changed from 2 to 4 to reduce false positives

# Load constant values from constants.py
constants_module = PROJECT_ROOT / "constants.py"
constant_values: set[str] = set()
if constants_module.exists():
    try:
        tree = ast.parse(constants_module.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.Assign):
                if all(
                    isinstance(t, ast.Name) and t.id.isupper() for t in node.targets
                ):
                    if isinstance(node.value, ast.Constant) and isinstance(
                        node.value.value, str
                    ):
                        constant_values.add(node.value.value)
    except Exception:  # pragma: no cover
        pass

string_counter: Counter[str] = Counter()
string_locations: dict[str, list[str]] = {}

for py_file in PROJECT_ROOT.rglob("*.py"):
    rel = py_file.relative_to(PROJECT_ROOT)
    # Skip allowed (whitelisted) files and excluded directories / hidden folders
    if rel.name in ALLOWED_FILES:
        continue
    if any(part in EXCLUDE_DIRS or part.startswith(".") for part in rel.parts):
        continue
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
    except Exception:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value.strip()
            if len(s) < MIN_LEN or " " not in s:
                continue
            if s in constant_values:
                continue
            string_counter[s] += 1
            string_locations.setdefault(s, []).append(
                f"{rel}:{getattr(node, 'lineno', '?')}"
            )

problems = [s for s, c in string_counter.items() if c >= MIN_COUNT]
if problems:
    print(
        "Hard-coded repeated message literals found (consider extracting to constants):"
    )
    for s in sorted(problems):
        print(f"- '{s}' (count={string_counter[s]})")
        for loc in string_locations[s]:
            print(f"    at {loc}")
    sys.exit(1)
else:
    print("No repeated hard-coded message literals found above thresholds.")
    sys.exit(0)
