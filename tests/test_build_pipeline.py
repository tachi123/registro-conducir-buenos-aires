"""Extract tests: scripts/extract.py parses cuestionario.txt text into raw
question blocks (structure only — no answers; answers are authored later).

Golden fixtures are VERBATIM slices of the real extraction
(%TEMP%\\opencode\\cuestionario.txt, from `pdftotext -layout cuestionario.pdf`):

- sample_preambulo.txt   src lines 22-126: footer "página 1", unnumbered
                         bullet V/F + A./B./C., wrapped stems/options,
                         footer "página 2" mid-sample
- sample_varias.txt      src lines 1465-1520: numbered 1)..3), multi-option
                         a)-g), footer "página 36" + "página 37", option c)
                         of Q1 misplaced after the footer (joins Q1)
- sample_senales.txt     src lines 3376-3430: heading, image stems, dash
                         options (a- b- c-), A) style options, "A -" style
- sample_vf_grid.txt     src lines 2494-2535: numbered 103-108 with columnar
                         "V        F" grids after the stems
- sample_mojibake.txt    synthetic double-encoded UTF-8 (Ã©, â€¢, Â¿)

srcPage rule (verified against the real file): the footer line
'página N de 228' is the LAST line of page N; content after it belongs to
page N+1.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"

import extract  # noqa: E402  (conftest.py adds scripts/ to sys.path)


def parse_text(name, section_slug="fixture"):
    with open(FIXTURES / name, encoding="utf-8") as fh:
        text = fh.read()
    return extract.parse_battery_text(text, src_file=name, section_slug=section_slug)


def test_mojibake_cleaned():
    """Spec: raw extraction containing Ã© must become correctly decoded accents."""
    blocks = extract.parse_battery_text(
        "¿Qué...? Ã© Ã¡ Ã³ Ã±\n\nA. OpciÃ³n uno.\nB. OpciÃ³n dos.",
        src_file="x.txt", section_slug="fixture",
    )
    assert len(blocks) == 1
    assert blocks[0]["question"] == "¿Qué...? é á ó ñ"
    assert blocks[0]["options"][0]["text"] == "Opción uno."
    assert blocks[0]["options"][1]["text"] == "Opción dos."


def test_mojibake_fixture_full():
    """Golden mojibake file: accents + bullet V/F + A. options decoded."""
    blocks = parse_text("sample_mojibake.txt", section_slug="intoxicacion")
    assert len(blocks) == 2
    q0 = blocks[0]
    assert q0["answerType"] == "single"
    assert q0["options"][0]["text"] == "Mayor reflejos y atención."
    assert q0["options"][2]["text"] == "Ningún efecto."
    q1 = blocks[1]
    assert q1["answerType"] == "truefalse"
    assert [o["key"] for o in q1["options"]] == ["v", "f"]
    assert q1["options"][0]["text"] == "Verdadero"
    assert q1["options"][1]["text"] == "Falso"


def test_unnumbered_blocks_and_bullet_vf():
    """Preambulo sample: unnumbered questions get sequential ids; bullet V/F
    becomes truefalse with v/f keys; wrapped option B joins its option."""
    blocks = parse_text("sample_preambulo.txt", section_slug="preambulo")
    assert len(blocks) >= 6
    q0 = blocks[0]
    assert q0["answerType"] == "truefalse"
    assert [o["key"] for o in q0["options"]] == ["v", "f"]
    # second question is A./B./C. single
    q1 = blocks[1]
    assert q1["answerType"] == "single"
    assert [o["key"] for o in q1["options"]] == ["a", "b", "c"]
    # a LATER question ("A fin de aumentar la propia seguridad...") carries a
    # WRAPPED option B: the indented continuation line joins option b
    wrapped = next(b for b in blocks if b["question"].startswith("A fin de aumentar"))
    assert [o["key"] for o in wrapped["options"]] == ["a", "b", "c"]
    assert wrapped["options"][1]["text"] == (
        "A las condiciones en que se encuentran: el automóvil, la "
        "infraestructura vial, las condiciones climáticas y el conductor."
    )
    # wrapped stem: two physical lines joined into one question text
    ambiental = next(b for b in blocks if b["question"].startswith(
        "El factor ambiental es el principal"))
    assert "meteorológicas o del camino" in ambiental["question"]
    # ids are sequential and unique, prefixed by section slug
    ids = [b["id"] for b in blocks]
    assert len(ids) == len(set(ids))
    assert ids == [f"preambulo-{i:04d}" for i in range(1, len(blocks) + 1)]


def test_src_page_tracked_from_footer():
    """Footer 'página N de 228' terminates page N; following content is page N+1."""
    blocks = parse_text("sample_preambulo.txt", section_slug="preambulo")
    # fixture starts with footer "página 1" -> questions are on page 2
    assert blocks[0]["srcPage"] == 2
    # after footer "página 2" (mid-sample) questions move to page 3
    pages = [b["srcPage"] for b in blocks]
    assert 2 in pages and 3 in pages
    # the first page-3 block is the one after the "página 2 de 228" line
    page3_first = next(b for b in blocks if b["srcPage"] == 3)
    assert "A fin de aumentar la propia seguridad" in page3_first["question"]


def test_numbered_questions_keep_number():
    """Numbered blocks preserve battery number; ids stay sequential. The
    fixture begins with the previous section's tail (unnumbered), so numbered
    questions are found by number."""
    blocks = parse_text("sample_varias.txt", section_slug="varias")
    numbered = [b for b in blocks if b["number"] is not None]
    assert [b["number"] for b in numbered] == [1, 2, 3]
    q2 = next(b for b in numbered if b["number"] == 2)
    assert [o["key"] for o in q2["options"]] == ["a", "b", "c", "d", "e", "f", "g"]
    assert q2["srcPage"] == 38  # after footer "página 37" (line 31 of fixture)


def test_misplaced_option_joins_open_question():
    """Option c) of Q1 is misplaced after the page footer by pdftotext; the
    parser must attach it to Q1 (still open) instead of dropping it."""
    blocks = parse_text("sample_varias.txt", section_slug="varias")
    q1 = next(b for b in blocks if b["number"] == 1)
    assert [o["key"] for o in q1["options"]] == ["a", "b", "c"]
    assert q1["options"][2]["text"] == (
        "Para todos los vehículos, excepto las motos, triciclos y cuatriciclos."
    )
    assert q1["srcPage"] == 37  # starts after footer "página 36" (line 1)


def test_dash_options_normalized():
    """Senales dash options (a- b- c-) normalize to keys a/b/c."""
    blocks = parse_text("sample_senales.txt", section_slug="senales")
    dashes = [b for b in blocks if "prioridad normativa" in b["question"]]
    assert len(dashes) == 1
    assert [o["key"] for o in dashes[0]["options"]] == ["a", "b", "c"]
    assert dashes[0]["options"][0]["text"].startswith("Ley vigente")


def test_multiple_option_styles_accepted():
    """A. / A) / 'A -' styles all produce lowercase keys."""
    blocks = parse_text("sample_senales.txt", section_slug="senales")
    styles = [b for b in blocks if "alcance reglamentario" in b["question"]]
    assert len(styles) == 1
    assert [o["key"] for o in styles[0]["options"]] == ["a", "b"]
    # trailing 'A - Restricción / B - información / C – Prevención' block
    azul = [b for b in blocks if "color azul" in b["question"]]
    assert len(azul) == 1
    assert [o["key"] for o in azul[0]["options"]] == ["a", "b", "c"]


def test_vf_columnar_grid():
    """Columnar 'V        F' grid after the stem => truefalse with v/f keys."""
    blocks = parse_text("sample_vf_grid.txt", section_slug="velocidades")
    tf = [b for b in blocks if b["answerType"] == "truefalse"]
    single = [b for b in blocks if b["answerType"] == "single"]
    assert len(tf) == 5  # 103, 105, 106, 107, 108
    assert len(single) == 1  # 104 only
    assert [o["key"] for o in tf[0]["options"]] == ["v", "f"]
    assert tf[0]["number"] == 103
    assert tf[-1]["number"] == 108


def test_metadata_markers_detected():
    """(Pregunta de carácter eliminatorio) -> essential; (Bahia Blanca) -> regionNote."""
    blocks = extract.parse_battery_text(
        "Pregunta con marcador\n\nA. Opción a.\nB. Opción b.\nC. Opción c.\n\n"
        "Otra pregunta (Pregunta de carácter eliminatorio)\n\n"
        "A. Sí.\nB. No.\n\n"
        "Pregunta regional (Bahia Blanca)\n\nA. X.\nB. Y.",
        src_file="x.txt", section_slug="fixture",
    )
    essential = [b for b in blocks if b["essential"]]
    regional = [b for b in blocks if b["regionNote"]]
    assert len(essential) == 1
    assert "Bahia Blanca" in regional[0]["regionNote"]


def test_image_stem_heuristic():
    """Stems referencing images get imageRequired=True; text-only stems get False."""
    blocks = extract.parse_battery_text(
        "La siguiente señal indica:\n\nA. Pare.\nB. Ceda el paso.\n\n"
        "¿A qué velocidad máxima se circula en ciudad?\n\nA. 40.\nB. 60.",
        src_file="x.txt", section_slug="fixture",
    )
    assert blocks[0]["imageRequired"] is True
    assert blocks[1]["imageRequired"] is False


def test_out_of_scope_excluded():
    """Moto/load sections never enter the in-scope raw output."""
    raw = extract.parse_battery_text(
        "Preguntas para la clase de motos:\n\n"
        "¿Casco obligatorio?\n\nA. Sí.\nB. No.",
        src_file="x.txt", section_slug="motos",
        in_scope=False,
    )
    assert raw == []


def test_parse_output_is_serializable_json():
    blocks = parse_text("sample_varias.txt", section_slug="varias")
    json.dumps(blocks)  # must not raise
    assert isinstance(blocks, list)
