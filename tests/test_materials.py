"""
Material summary cards tests.

The app ships exactly 5 cards, one per study material, each with the four
content fields (title, queEs, queEstudiar, peso). Card content lives in
data/materials.json — this test guards structure and the weight hierarchy.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATERIALS_PATH = ROOT / "data" / "materials.json"

EXPECTED_IDS = ["cuestionario", "manual", "ansv-senales", "ley-24449", "ley-13927"]

REQUIRED_FIELDS = ["id", "title", "queEs", "queEstudiar", "peso"]


def _load_materials():
    with open(MATERIALS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


MATERIALS = _load_materials()


def test_exactly_five_cards():
    assert len(MATERIALS) == 5


def test_cards_have_the_five_ids():
    ids = {card["id"] for card in MATERIALS}
    assert ids == set(EXPECTED_IDS)


def test_each_card_has_four_content_fields_plus_id():
    for card in MATERIALS:
        for field in REQUIRED_FIELDS:
            assert field in card, f"{card.get('id')} missing field {field}"
        assert card["title"], card.get("id")
        assert card["queEs"], card.get("id")
        assert card["queEstudiar"], card.get("id")
        assert isinstance(card["peso"], int)


def test_cuestionario_ranks_highest():
    """Cuestionario oficial has peso 1 = highest rank among the five."""
    pesos = {card["id"]: card["peso"] for card in MATERIALS}
    assert pesos["cuestionario"] == 1
    others = [p for i, p in pesos.items() if i != "cuestionario"]
    assert all(p > pesos["cuestionario"] for p in others)


def test_peso_is_a_rank_1_to_5():
    pesos = {card["id"]: card["peso"] for card in MATERIALS}
    assert sorted(pesos.values()) == [1, 2, 3, 4, 5]