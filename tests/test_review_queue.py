"""
Confidence-report / review-queue tests.

Contract (design.md + question-bank spec):
- scripts/confidence_report.py derives data/review-queue.json from the shipped
  bank + the raw extraction. "Never publish unreviewed answers."
- A question is queued when ANY of:
  1. it was extracted (in-scope) but has NO authored answer (missing authoring);
  2. its confidence is below the gate (CONFIDENCE_GATE default 0.9);
  3. it is not marked reviewed.
- The queue carries per-question reasons so humans can act; the deploy
  workflow fails while the queue is non-empty.
- Questions at/above gate AND reviewed AND authored are NOT queued.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "build_bank"
EXTRACTED = FIXTURES / "extracted"
AUTHORING = FIXTURES / "authoring"
SCHEMA_PATH = ROOT / "data" / "schema" / "question.schema.json"

import build_bank  # noqa: E402
import confidence_report  # noqa: E402


@pytest.fixture(scope="module")
def bank_dir(tmp_path_factory):
    """Shipped bank built from the shared build_bank fixtures."""
    out = tmp_path_factory.mktemp("bank_out")
    build_bank.build_bank(EXTRACTED, AUTHORING, SCHEMA_PATH, out)
    return out


@pytest.fixture(scope="module")
def queue_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("queue_out")


@pytest.fixture(scope="module")
def report(bank_dir, queue_dir):
    return confidence_report.generate(EXTRACTED, bank_dir, queue_dir, gate=0.9)


def test_report_returns_entries(report):
    entries = report["entries"]
    # from the fixture: senales-226 (no authoring), seguridad-002 (low conf + unreviewed)
    assert {e["id"] for e in entries} == {"senales-226", "seguridad-002"}


def test_missing_authoring_entry_has_reason(report):
    entry = next(e for e in report["entries"] if e["id"] == "senales-226")
    assert "missing" in entry["reasons"]
    assert entry["confidence"] is None
    assert entry["srcPage"] is not None


def test_low_confidence_and_unreviewed_reasons(report):
    entry = next(e for e in report["entries"] if e["id"] == "seguridad-002")
    assert "low-confidence" in entry["reasons"]
    assert "unreviewed" in entry["reasons"]
    assert entry["confidence"] == 0.7


def test_confident_reviewed_question_not_queued(report):
    ids = {e["id"] for e in report["entries"]}
    assert "seguridad-001" not in ids  # 0.9, reviewed
    assert "senales-225a" not in ids  # 0.9, reviewed
    assert "auto-5001" not in ids  # 0.9, reviewed


def test_queue_file_written_with_gate_and_count(queue_dir, report):
    with open(queue_dir / "review-queue.json", encoding="utf-8") as fh:
        data = json.load(fh)
    assert data["gate"] == 0.9
    assert data["count"] == 2
    assert len(data["entries"]) == 2


def test_gate_raise_flags_more(tmp_path):
    """TRIANGULATE: raising the gate to 0.95 must also queue the 0.9 items."""
    bank = tmp_path / "bank"
    build_bank.build_bank(EXTRACTED, AUTHORING, SCHEMA_PATH, bank)
    stricter = confidence_report.generate(EXTRACTED, bank, tmp_path, gate=0.95)
    ids = {e["id"] for e in stricter["entries"]}
    assert "seguridad-001" in ids  # 0.9 < 0.95 now flagged
    assert "senales-225a" in ids  # 0.9 < 0.95 now flagged
    assert "auto-5001" in ids  # 0.9 < 0.95 now flagged


def test_gate_lower_keeps_high_confidence_clear(tmp_path):
    """TRIANGULATE: gate 0.6 clears the 0.7 unreviewed/low item? NO — it stays
    queued because it is unreviewed; the confidence reason just drops."""
    bank = tmp_path / "bank"
    build_bank.build_bank(EXTRACTED, AUTHORING, SCHEMA_PATH, bank)
    relaxed = confidence_report.generate(EXTRACTED, bank, tmp_path, gate=0.6)
    entry = next(e for e in relaxed["entries"] if e["id"] == "seguridad-002")
    assert "low-confidence" not in entry["reasons"]  # 0.7 >= 0.6
    assert "unreviewed" in entry["reasons"]  # still unreviewed