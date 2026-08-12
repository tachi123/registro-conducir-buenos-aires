"""
confidence_report.py — derive data/review-queue.json from the shipped bank and
the raw extraction. Deploy gate: fail while the queue is non-empty.

A question is queued when ANY of:
1. extracted (in-scope) but absent from the shipped bank (missing authoring);
2. confidence below CONFIDENCE_GATE (default 0.9);
3. not marked reviewed.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import build_bank


def _load_json(path: Path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def generate(
    extracted_dir: Path,
    bank_dir: Path,
    output_dir: Path,
    gate: float = 0.9,
) -> dict:
    """Scan extraction + shipped bank, return report dict, write review-queue.json."""
    shipped: dict = {}
    for name in build_bank.CATEGORY_FILE.values():
        path = bank_dir / name
        if not path.exists():
            continue
        for q in _load_json(path):
            shipped[q["id"]] = q

    entries: List[dict] = []
    for section in sorted(build_bank.IN_SCOPE_SECTIONS):
        path = extracted_dir / f"{section}.json"
        if not path.exists():
            continue
        for q in _load_json(path):
            reasons = []
            shipped_q = shipped.get(q["id"])
            if shipped_q is None:
                entries.append({
                    "id": q["id"], "section": section, "srcPage": q["srcPage"],
                    "confidence": None, "reviewed": False,
                    "reasons": ["missing"],
                })
                continue
            if shipped_q["confidence"] < gate:
                reasons.append("low-confidence")
            if not shipped_q["reviewed"]:
                reasons.append("unreviewed")
            if reasons:
                entries.append({
                    "id": q["id"], "section": section,
                    "srcPage": shipped_q["srcPage"],
                    "confidence": shipped_q["confidence"],
                    "reviewed": shipped_q["reviewed"],
                    "reasons": reasons,
                })

    report = {
        "gate": gate,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "count": len(entries),
        "entries": sorted(entries, key=lambda e: e["id"]),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "review-queue.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    root = Path(__file__).resolve().parents[1]
    extracted_dir = Path(argv[0]) if argv else root / "data" / "_extracted"
    bank_dir = Path(argv[1]) if len(argv) > 1 else root / "data"
    output_dir = Path(argv[2]) if len(argv) > 2 else root / "data"
    gate = float(argv[3]) if len(argv) > 3 else 0.9
    report = generate(extracted_dir, bank_dir, output_dir, gate=gate)
    print(
        f"review queue: {report['count']} question(s) need review "
        f"(gate {report['gate']}) -> {output_dir / 'review-queue.json'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())