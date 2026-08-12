"""
Build-bank tests: scripts/build_bank.py merges extraction structure
(data/_extracted/*.json) with the authored answer overlay (data/authoring/*.json)
and emits the three shipped category files plus data/index.json.

Contract (design.md + question-bank spec):
- 3 category files: generales.json, senales.json, auto.json (categories ARE
  the sampling strata).
- Out-of-scope sections (moto, cargas, ...) are excluded from every file.
- Questions without an authored overlay entry cannot satisfy the schema
  (correct/fundamento/sources required) -> NOT shipped; ids reported as missing.
- Emitted questions are schema-valid (extraction-internal fields line_no and
  triage_note must be stripped; authored fields merged in).
- index.json: {version, generated, sections:{slug->{category,count}},
  categories:{...counts}}.
"""
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "build_bank"
EXTRACTED = FIXTURES / "extracted"
AUTHORING = FIXTURES / "authoring"
SCHEMA_PATH = ROOT / "data" / "schema" / "question.schema.json"

import build_bank  # noqa: E402  (conftest.py adds scripts/ to sys.path)


@pytest.fixture(scope="module")
def result(tmp_path_factory):
    out = tmp_path_factory.mktemp("bank_out")
    summary = build_bank.build_bank(EXTRACTED, AUTHORING, SCHEMA_PATH, out)
    return out, summary


def _load(out, name):
    with open(out / name, encoding="utf-8") as fh:
        return json.load(fh)


def test_emits_three_category_files(result):
    out, _ = result
    for name in ["generales.json", "senales.json", "auto.json"]:
        assert (out / name).exists(), f"missing shipped file {name}"


def test_category_file_contents(result):
    out, _ = result
    generales = _load(out, "generales.json")
    senales = _load(out, "senales.json")
    auto = _load(out, "auto.json")
    assert [q["id"] for q in generales] == ["seguridad-001", "seguridad-002"]
    assert [q["id"] for q in senales] == ["senales-225a", "senales-225b"]
    assert [q["id"] for q in auto] == ["auto-5001"]


def test_out_of_scope_section_excluded(result):
    out, _ = result
    for name in ["generales.json", "senales.json", "auto.json"]:
        ids = [q["id"] for q in _load(out, name)]
        assert not any(i.startswith("motos") for i in ids), f"motos leaked into {name}"


def test_unanswered_question_not_shipped_and_reported_missing(result):
    out, summary = result
    all_ids = [q["id"] for f in ["generales.json", "senales.json", "auto.json"]
               for q in _load(out, f)]
    assert "senales-226" not in all_ids  # extracted but no overlay entry
    assert "senales-226" in summary["missing"]


def test_emitted_questions_pass_schema(result):
    out, _ = result
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        schema = json.load(fh)
    for name in ["generales.json", "senales.json", "auto.json"]:
        for q in _load(out, name):
            jsonschema.validate(q, schema)


def test_extraction_internal_fields_stripped(result):
    out, _ = result
    for q in _load(out, "generales.json"):
        assert "line_no" not in q
        assert "triage_note" not in q


def test_authored_fields_merged(result):
    out, _ = result
    q = next(x for x in _load(out, "generales.json") if x["id"] == "seguridad-001")
    assert q["correct"] == "v"
    assert q["answerType"] == "truefalse"  # from extraction options shape
    assert q["confidence"] == 0.9
    assert q["reviewed"] is True
    assert q["essential"] is True  # overlay overrides extraction default
    assert q["subcategory"] == "siniestros"  # overlay overrides section slug
    assert q["fundamento"].startswith("Señalizar")
    assert q["sources"][0]["material"] == "manual"
    assert q["srcPage"] == 18  # extraction field preserved
    assert q["srcFile"] == "cuestionario.pdf"


def test_image_question_carries_image_ref(result):
    out, _ = result
    q = next(x for x in _load(out, "senales.json") if x["id"] == "senales-225a")
    assert q["imageRequired"] is True
    assert q["imageRef"] == "assets/signs/senales-225a.png"


def test_index_json_structure(result):
    out, _ = result
    index = _load(out, "index.json")
    assert index["version"] == 1
    assert "generated" in index
    assert index["sections"] == {
        "seguridad": {"category": "generales", "count": 2},
        "senales": {"category": "senales", "count": 2},
        "auto": {"category": "especificas-auto", "count": 1},
    }
    assert index["categories"] == {
        "generales": 2, "senales": 2, "especificas-auto": 1,
    }


def test_low_confidence_question_still_ships_with_flag(result):
    """Design: inline confidence+reviewed per question; the review GATE lives in
    confidence_report.py (review-queue), not in the shipped bank."""
    out, _ = result
    q = next(x for x in _load(out, "generales.json") if x["id"] == "seguridad-002")
    assert q["confidence"] == 0.7
    assert q["reviewed"] is False
