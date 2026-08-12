"""
Schema integrity tests for the Clase B question bank.

Validates the bank-sample fixture always, and the real shipped bank files
(data/{generales,senales,auto}.json) when they exist (they are produced by
build_bank.py; until then the fixture is the ground truth).
"""
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data" / "schema" / "question.schema.json"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "bank-sample.json"
BANK_FILES = ["generales.json", "senales.json", "auto.json"]

CATEGORIES = {"generales", "senales", "especificas-auto"}
SECTIONS = {
    "preambulo", "seguridad", "documentacion", "intoxicacion", "varias",
    "semaforo", "velocidades", "adelantamiento", "autopistas",
    "estacionamiento", "luces", "giros", "senales", "conduccion",
    "seg-activa", "auto",
}


@pytest.fixture(scope="module")
def schema():
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def fixture_bank():
    with open(FIXTURE_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def _load_bank_files():
    """Return list of (filename, questions) for shipped bank files present."""
    out = []
    for name in BANK_FILES:
        path = ROOT / "data" / name
        if path.exists():
            with open(path, encoding="utf-8") as fh:
                out.append((name, json.load(fh)))
    return out


REAL_BANKS = _load_bank_files()
REAL_BANK_IDS = [f"{name}:{q['id']}" for name, questions in REAL_BANKS for q in questions]


@pytest.fixture(params=[("fixture", None)] + [(n, n) for n, _ in REAL_BANKS])
def bank(request):
    """Yields (bank_name, questions) for each available bank source."""
    name, path = request.param
    if name == "fixture":
        return name, request.getfixturevalue("fixture_bank")
    with open(ROOT / "data" / path, encoding="utf-8") as fh:
        return name, json.load(fh)


def test_schema_file_is_valid_json_schema(schema):
    # draft-07 resolution: every object in the schema is itself valid JSON
    jsonschema.Draft7Validator.check_schema(schema)


def test_every_question_conforms_to_schema(schema, bank):
    _, questions = bank
    assert len(questions) > 0  # a bank source with zero questions proves nothing
    for q in questions:
        jsonschema.validate(q, schema)


def test_ids_unique_across_bank(schema, bank):
    _, questions = bank
    ids = [q["id"] for q in questions]
    assert len(ids) == len(set(ids)), f"duplicate ids: {[i for i in ids if ids.count(i) > 1]}"


def test_id_format_section_seq(schema, bank):
    _, questions = bank
    for q in questions:
        section, _, seq = q["id"].rpartition("-")
        assert section in SECTIONS, f"id {q['id']} has unknown section {section!r}"
        # seq may carry a trailing letter for image-pair duplicates (senales-225a)
        assert seq[: len(seq) - 1].isdigit() if seq[-1].isalpha() else seq.isdigit()


def test_number_gaps_and_duplicates_tolerated(schema, bank):
    """Duplicates (e.g. 225 image pair) and gaps (34, 193) must not break loading."""
    _, questions = bank
    numbers = [q["number"] for q in questions if q["number"] is not None]
    # duplicates are legal; float(int) comparison must be consistent
    for q in questions:
        if q["number"] is not None:
            assert isinstance(q["number"], int)


def test_correct_in_options(schema, bank):
    _, questions = bank
    for q in questions:
        keys = {opt["key"] for opt in q["options"]}
        assert q["correct"] in keys, f"{q['id']}: correct {q['correct']!r} not in {keys}"


def test_option_keys_unique_within_question(schema, bank):
    _, questions = bank
    for q in questions:
        keys = [opt["key"] for opt in q["options"]]
        assert len(keys) == len(set(keys)), f"{q['id']} has duplicate option keys"


def test_enums(schema, bank):
    _, questions = bank
    for q in questions:
        assert q["category"] in CATEGORIES, q["id"]
        assert q["answerType"] in {"single", "truefalse"}, q["id"]
        assert isinstance(q["essential"], bool), q["id"]
        assert isinstance(q["imageRequired"], bool), q["id"]
        assert isinstance(q["reviewed"], bool), q["id"]
        assert 0.0 <= q["confidence"] <= 1.0, q["id"]


def test_truefalse_shape(schema, bank):
    _, questions = bank
    for q in questions:
        if q["answerType"] == "truefalse":
            keys = sorted(opt["key"] for opt in q["options"])
            assert keys == ["f", "v"], (
                f"{q['id']}: V/F options must be keys v/f, got {keys}"
            )
            assert q["correct"] in {"v", "f"}, q["id"]


def test_single_shape(schema, bank):
    _, questions = bank
    for q in questions:
        if q["answerType"] == "single":
            assert len(q["options"]) >= 2, q["id"]


def test_image_required_rules(schema, bank):
    """imageRequired => question not answerable from text alone: imageRef may be
    null (placeholder + srcPage link) but srcPage must exist to study the visual."""
    _, questions = bank
    for q in questions:
        if q["imageRequired"]:
            assert q["srcPage"] is not None, f"{q['id']} imageRequired needs srcPage"
        else:
            # non-image questions carry no image reference
            assert q["imageRef"] is None, f"{q['id']} has imageRef but not imageRequired"


def test_sources_and_fundamento(schema, bank):
    """Shipped questions must carry fundamento + at least one source."""
    _, questions = bank
    for q in questions:
        assert q["fundamento"], f"{q['id']} missing fundamento"
        assert len(q["sources"]) >= 1, f"{q['id']} missing sources"
        for src in q["sources"]:
            assert src["material"], f"{q['id']} source missing material"
            assert src["ref"], f"{q['id']} source missing ref"