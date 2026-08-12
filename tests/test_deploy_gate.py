"""
Deploy gate tests (task 5.1): review_gate.py blocks publishing while
data/review-queue.json lists pending questions, and passes when empty.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
import review_gate  # noqa: E402  (conftest.py adds scripts/ to sys.path)


def _write_queue(tmp_path, count, entries=()):
    q = tmp_path / "review-queue.json"
    q.write_text(
        json.dumps({"gate": 0.9, "count": count, "entries": list(entries)}),
        encoding="utf-8",
    )
    return q


def test_nonempty_queue_blocks_deploy(tmp_path):
    q = _write_queue(tmp_path, 2, [{"id": "senales-226"}, {"id": "seguridad-002"}])
    assert review_gate.gate(q) == 1


def test_empty_queue_allows_deploy(tmp_path):
    q = _write_queue(tmp_path, 0)
    assert review_gate.gate(q) == 0


def test_missing_queue_allows_deploy(tmp_path):
    assert review_gate.gate(tmp_path / "does-not-exist.json") == 0


def test_gate_reads_count_not_entries(tmp_path):
    """TRIANGULATE: count is the source of truth (entries may be truncated)."""
    q = _write_queue(tmp_path, 1, [{"id": "only-one"}])
    assert review_gate.gate(q) == 1
