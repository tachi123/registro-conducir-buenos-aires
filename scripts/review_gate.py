"""
review_gate.py — deploy gate: fail (nonzero exit) while data/review-queue.json
lists questions that still need review. The Pages workflow runs this before
publishing: never publish unreviewed answers (design.md rollout gate).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Optional


def gate(queue_path: Path) -> int:
    """Return 0 if deployable, 1 if the review queue is non-empty."""
    if not queue_path.exists():
        print("review-queue.json not found — assuming deployable (run the build first).")
        return 0
    data = json.loads(queue_path.read_text(encoding="utf-8"))
    count = data.get("count", 0)
    if count > 0:
        ids = ", ".join(e["id"] for e in data.get("entries", [])[:5])
        print(f"DEPLOY BLOCKED: {count} question(s) still in the review queue ({ids}...).")
        return 1
    print("review queue empty — deploy OK.")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    queue_path = Path(argv[0]) if argv else (
        Path(__file__).resolve().parents[1] / "data" / "review-queue.json"
    )
    return gate(queue_path)


if __name__ == "__main__":
    raise SystemExit(main())
