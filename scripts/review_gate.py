"""
review_gate.py — deploy gate: fail (nonzero exit) ONLY when a shipped bank
file is missing or empty, or data/index.json is missing. The review queue is
informational: pending low-confidence reviews are reported, never blocking.

Contract (relaxed per user feedback): the bank is the product; a non-empty
review queue with legitimately lower-confidence answers must not prevent the
user from deploying the site.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Optional

BANK_FILES = ["generales.json", "senales.json", "auto.json"]


def gate(bank_dir: Path) -> int:
    """Return 0 if deployable, 1 if a bank file is missing/empty or index.json missing."""
    problems: List[str] = []

    for name in BANK_FILES:
        path = bank_dir / name
        if not path.exists():
            problems.append(f"data/{name} is missing")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if not data:
            problems.append(f"data/{name} is empty")

    index = bank_dir / "index.json"
    if not index.exists():
        problems.append("data/index.json is missing")

    if problems:
        print("DEPLOY BLOCKED:")
        for p in problems:
            print(f"  - {p}")
        return 1

    print("bank files present and non-empty — deploy OK.")
    return 0


def report_queue(bank_dir: Path) -> None:
    """Informational: print the pending review count, never block on it."""
    queue = bank_dir / "review-queue.json"
    if not queue.exists():
        print("review-queue.json not found (run confidence_report.py to regenerate).")
        return
    data = json.loads(queue.read_text(encoding="utf-8"))
    count = data.get("count", 0)
    if count > 0:
        print(f"NOTE (informational): {count} question(s) pending review — does not block deploy.")
    else:
        print("review queue empty.")


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    bank_dir = Path(argv[0]) if argv else (
        Path(__file__).resolve().parents[1] / "data"
    )
    report_queue(bank_dir)
    return gate(bank_dir)


if __name__ == "__main__":
    raise SystemExit(main())
