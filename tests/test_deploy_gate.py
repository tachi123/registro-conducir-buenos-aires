"""
Deploy gate tests (task 5.1, relaxed): review_gate.py blocks publishing ONLY
when a shipped bank file (data/{generales,senales,auto}.json) is missing or
empty, or data/index.json is missing. The review queue is informational:
pending low-confidence reviews must NOT block deploy.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
import review_gate  # noqa: E402  (conftest.py adds scripts/ to sys.path)


def _write_bank(tmp_path, *, generales=True, senales=True, auto=True, index=True,
                empty_generales=False, empty_senales=False, empty_auto=False):
    """Write a default-populated bank dir; flags control what is present."""
    if generales:
        (tmp_path / "generales.json").write_text("[]" if empty_generales else '[{"id": "g1"}]', encoding="utf-8")
    if senales:
        (tmp_path / "senales.json").write_text("[]" if empty_senales else '[{"id": "s1"}]', encoding="utf-8")
    if auto:
        (tmp_path / "auto.json").write_text("[]" if empty_auto else '[{"id": "a1"}]', encoding="utf-8")
    if index:
        (tmp_path / "index.json").write_text('{"version": 1}', encoding="utf-8")
    return tmp_path


def _write_queue(tmp_path, count):
    q = tmp_path / "review-queue.json"
    q.write_text(
        json.dumps({"gate": 0.9, "count": count, "entries": [{"id": "x"}] if count else []}),
        encoding="utf-8",
    )
    return q


def test_missing_bank_file_blocks(tmp_path):
    _write_bank(tmp_path, senales=False)
    assert review_gate.gate(tmp_path) == 1


def test_missing_index_blocks(tmp_path):
    _write_bank(tmp_path, index=False)
    assert review_gate.gate(tmp_path) == 1


def test_empty_bank_file_blocks(tmp_path):
    _write_bank(tmp_path, empty_generales=True)
    assert review_gate.gate(tmp_path) == 1


def test_populated_bank_allows_deploy(tmp_path):
    _write_bank(tmp_path)
    assert review_gate.gate(tmp_path) == 0


def test_empty_dir_blocks(tmp_path):
    assert review_gate.gate(tmp_path) == 1


def test_pending_reviews_do_not_block(tmp_path):
    """RELAXED: a non-empty review queue must NOT block deploy anymore."""
    _write_bank(tmp_path)
    _write_queue(tmp_path, 2)
    assert review_gate.gate(tmp_path) == 0


def test_missing_queue_still_allows_deploy(tmp_path):
    _write_bank(tmp_path)
    assert review_gate.gate(tmp_path) == 0
