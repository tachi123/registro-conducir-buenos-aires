"""
build_bank.py — merge extraction structure with authored answers into the
three shipped category files + data/index.json.

Contract (design.md + question-bank spec):
- Input: data/_extracted/<section>.json (from extract.py, gitignored) and the
  authored overlay data/authoring/<file>.json keyed by question id.
- The overlay provides correct, fundamento, sources[], confidence, reviewed and
  may override essential, subcategory, imageRef. Extraction supplies the rest.
- Questions without an overlay entry cannot satisfy the schema (correct,
  fundamento, sources[] are required) -> they are NOT shipped and their ids are
  reported in the returned summary as "missing".
- Out-of-scope sections (motos, cargas, ...) are excluded from every file.
- Emitted questions are schema-validated; extraction-internal fields
  (line_no, triage_note) are stripped.

Usage:
    python scripts/build_bank.py [EXTRACTED_DIR] [AUTHORING_DIR] [SCHEMA] [OUTPUT_DIR]
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import jsonschema

# ---------------------------------------------------------------------------
# In-scope Clase B sections (schema enum). Anything else is out of scope.
# ---------------------------------------------------------------------------
IN_SCOPE_SECTIONS = {
    "preambulo", "seguridad", "documentacion", "intoxicacion", "varias",
    "semaforo", "velocidades", "adelantamiento", "autopistas",
    "estacionamiento", "luces", "giros", "senales", "conduccion",
    "seg-activa", "auto",
}

CATEGORY_FILE = {
    "generales": "generales.json",
    "senales": "senales.json",
    "especificas-auto": "auto.json",
}

_STRIPPED = {"line_no", "triage_note"}

_OVERLAY_OVERRIDES = {"essential", "subcategory", "imageRef", "imageRequired"}


def _load_json(path: Path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _load_overlays(authoring_dir: Path) -> Dict[str, dict]:
    """Flatten every authoring file into {question_id: overlay}."""
    overlay: Dict[str, dict] = {}
    if not authoring_dir.exists():
        return overlay
    for path in sorted(authoring_dir.glob("*.json")):
        data = _load_json(path)
        if isinstance(data, dict):
            overlay.update(data)
        else:  # tolerate a bare list of {id, ...} entries
            for entry in data:
                overlay[entry["id"]] = entry
    return overlay


def _merge(extracted: dict, authored: dict) -> dict:
    """Produce the final schema-conformant question object."""
    q = {k: v for k, v in extracted.items() if k not in _STRIPPED}
    for field in ("correct", "fundamento", "sources", "confidence", "reviewed"):
        q[field] = authored[field]
    for field in _OVERLAY_OVERRIDES:
        if field in authored:
            q[field] = authored[field]
    return q


def build_bank(
    extracted_dir: Path,
    authoring_dir: Path,
    schema_path: Path,
    output_dir: Path,
) -> dict:
    """Build the three category files + index.json. Returns a summary dict."""
    schema = _load_json(schema_path)
    overlay = _load_overlays(authoring_dir)

    shipped: Dict[str, List[dict]] = {"generales": [], "senales": [], "especificas-auto": []}
    section_counts: Dict[str, dict] = {}
    missing: List[str] = []
    excluded_sections: List[str] = []

    for path in sorted(extracted_dir.glob("*.json")):
        section = path.stem
        if section not in IN_SCOPE_SECTIONS:
            excluded_sections.append(section)
            continue
        for q in _load_json(path):
            authored = overlay.get(q["id"])
            if authored is None:
                missing.append(q["id"])
                continue
            merged = _merge(q, authored)
            jsonschema.validate(merged, schema)
            shipped[merged["category"]].append(merged)

    # section -> {category, count} derived from what actually shipped
    section_counts = {}
    for cat, questions in shipped.items():
        for q in questions:
            entry = section_counts.setdefault(q["section"], {"category": cat, "count": 0})
            entry["count"] += 1

    output_dir.mkdir(parents=True, exist_ok=True)
    for cat, filename in CATEGORY_FILE.items():
        (output_dir / filename).write_text(
            json.dumps(shipped[cat], ensure_ascii=False, indent=2), encoding="utf-8"
        )

    index = {
        "version": 1,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sections": section_counts,
        "categories": {cat: len(qs) for cat, qs in shipped.items()},
    }
    (output_dir / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return {
        "shipped": {cat: len(qs) for cat, qs in shipped.items()},
        "missing": missing,
        "excluded_sections": excluded_sections,
    }


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    root = Path(__file__).resolve().parents[1]
    extracted_dir = Path(argv[0]) if argv else root / "data" / "_extracted"
    authoring_dir = Path(argv[1]) if len(argv) > 1 else root / "data" / "authoring"
    schema_path = Path(argv[2]) if len(argv) > 2 else root / "data" / "schema" / "question.schema.json"
    output_dir = Path(argv[3]) if len(argv) > 3 else root / "data"
    summary = build_bank(extracted_dir, authoring_dir, schema_path, output_dir)
    print(
        f"bank built: {summary['shipped']} shipped; "
        f"{len(summary['missing'])} missing authoring; "
        f"excluded sections {summary['excluded_sections']} -> {output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
