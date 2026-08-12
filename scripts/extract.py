"""
extract.py — parse the official Clase B battery text (cuestionario.txt, from
`pdftotext -layout`) into raw structured question blocks.

Design contract (spec "Extraction and build pipeline"):
- Regenerates STRUCTURE only. Correct answers, fundamento, sources and
  confidence are authored separately (see build_bank.py + data/authoring).
- Cleans mojibake (double-encoded UTF-8 such as "Ã©" -> "é") defensively; the
  real extraction is clean UTF-8 so that pass is a no-op there.
- Detects V/F questions: bullet ("• Verdadero." / "• Falso.") AND columnar
  grids ("V        F" right after the stem). Both normalize to keys v/f.
- Assigns sequential ids per section: {section}-{seq}.
- srcPage rule (verified against the real file): the footer line
  "página N de 228" is the LAST line of page N, so content AFTER it belongs
  to page N+1.
- Flags metadata markers: "(Pregunta de carácter eliminatorio)" -> essential,
  "(Bahia Blanca)" -> regionNote, image-referencing stems -> imageRequired.

Usage:
    python scripts/extract.py [INPUT_TXT] [OUTPUT_DIR]
The full-battery section map (SECTION_MAP) drives the production run; the
public parse_battery_text() above is what tests exercise.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Section map: (slug, category, in_scope, line_start, line_end) 1-based lines
# of the full extraction. Line ranges verified against cuestionario.txt
# (section headings "Preguntas para todas las clases: ...").
# ---------------------------------------------------------------------------
SECTION_MAP = [
    ("preambulo", "generales", True, 34, 666),
    ("seguridad", "generales", True, 667, 849),
    ("documentacion", "generales", True, 850, 1055),
    ("intoxicacion", "generales", True, 1056, 1484),
    ("varias", "generales", True, 1485, 2248),
    ("semaforo", "generales", True, 2249, 2368),
    ("velocidades", "generales", True, 2369, 2661),
    ("adelantamiento", "generales", True, 2662, 2794),
    ("autopistas", "generales", True, 2795, 2925),
    ("estacionamiento", "generales", True, 2992, 3092),
    ("luces", "generales", True, 3093, 3221),
    ("giros", "generales", True, 3222, 3375),
    ("senales", "senales", True, 3376, 4608),
    ("conduccion", "generales", True, 4609, 6398),
    ("seg-activa", "generales", True, 6399, 6486),
    ("auto", "especificas-auto", True, 6489, 7398),
    # Out-of-scope class sections (never shipped):
    ("traccion-sangre", None, False, 2926, 2991),
    ("camionetas-carga", None, False, 7399, 7655),
    ("motos", None, False, 7656, 8185),
    ("urgencia", None, False, 8186, 8469),
    ("taxis", None, False, 8470, 8623),
    ("cargas", None, False, 8624, 9362),
    ("camion-sin-acoplado", None, False, 9363, 9568),
    ("camiones-acoplado", None, False, 9569, 9925),
    ("pasajeros", None, False, 9926, 10180),
]


# ---------------------------------------------------------------------------
# Mojibake cleaning (defensive; real extraction is already clean UTF-8)
# ---------------------------------------------------------------------------
_DOUBLE_ENCODED = {
    "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ã³": "ó", "Ãº": "ú", "Ã¼": "ü",
    "Ã±": "ñ", "Ã": "À", "Â": "",  # fallbacks dropped below if unused
    "Â¿": "¿", "Â¡": "¡",
    "â€¢": "•", "â€œ": "“", "â€\x9d": "”", "â€“": "–", "â€”": "—",
}
# Order keys by length descending so multi-byte sequences match first.
_MOJI_KEYS = sorted(_DOUBLE_ENCODED, key=len, reverse=True)
_MOJI_RE = re.compile("|".join(re.escape(k) for k in _MOJI_KEYS))


def clean_text(text: str) -> str:
    """Normalize and de-mojibake a piece of extracted text."""
    text = text.replace("\x0c", "\n")  # form feeds are page breaks
    text = _MOJI_RE.sub(lambda m: _DOUBLE_ENCODED[m.group(0)], text)
    return text


# ---------------------------------------------------------------------------
# Pattern helpers
# ---------------------------------------------------------------------------
_NOISE_RE = re.compile(
    r"^\s*(IF-2019-33101289-GDEBA-DPPYSVMGGP|"
    r"BATER\u00cdA DE PREGUNTAS Y RESPUESTAS|"
    r"Direcci\u00f3n Provincial|de Pol\u00edtica y Seguridad Vial|"
    r"G O B I E R N O|2019 - A\u00f1o del centenario|Hoja Adicional|"
    r"N\u00fameros:|LA PLATA|Lunes 23 de Septiembre|Referencia:|\d+\s*p\u00e1gina)",
    re.IGNORECASE,
)
_HEADING_RE = re.compile(
    r"^\s*(\d+\)\s*)?(Preguntas para todas las clases|Preguntas para la clase de|"
    r"Preguntas para el |Preguntas para clase de|Preguntas para camionetas|"
    r"Preguntas para Camion|Preguntas para camiones|Preguntas para la clase de motos|"
    r"Preguntas para servicios|Taxis y Remises|Veh\u00edculos afectados|"
    r"Preguntas para Traccion|SE\u00d1ALES DE TRANSITO|PREGUNTAS GENERALES|"
    r"PREGUNTAS ESPEC\u00cdFICAS SEG\u00daN CLASE|Anexo I:)",
    re.IGNORECASE,
)
_FOOTER_RE = re.compile(r"p\u00e1gina (\d+) de 228")
_NUMBERED_RE = re.compile(r"^(\d+)\)\s*(.*)")
_OPTION_RE = re.compile(r"^([a-zA-Z])\s*[\.\)\-\u2013]\s*(.*)")
_BULLET_VF_RE = re.compile(r"^\u2022?\s*(Verdadero|Falso)\.?\s*$", re.IGNORECASE)
_COLUMNAR_VF_RE = re.compile(r"^\s*V\s+F\s*$")
_ELIMINATORIO_RE = re.compile(r"\(?Pregunta de car\u00e1cter eliminatorio\)?", re.IGNORECASE)
_REGION_RE = re.compile(r"\((Bahia Blanca|Bah\u00eda Blanca)\)", re.IGNORECASE)
_IMAGE_STEM_RE = re.compile(
    r"(siguiente se\u00f1al indica|la siguiente imagen|indique cu\u00e1l de estas im\u00e1genes|"
    r"la siguiente figura|en la imagen|figura a|figura b|visualiza en la imagen|"
    r"muestra la imagen|las siguientes im\u00e1genes|la imagen corresponde)",
    re.IGNORECASE,
)


def _join_wrapped(prev: str, nxt: str) -> str:
    """Join a wrapped option continuation line.

    pdftotext splits wrapped lines two ways (both verified in the real file):
    - mid-word split with a trailing hyphen artifact: "condi-" + "ciones"
      -> "condiciones" (no space, hyphen dropped);
    - clean word-boundary wrap: "en ocasi\u00f3n" + "de circulaci\u00f3n"
      -> "en ocasi\u00f3n de circulaci\u00f3n" (single space).
    """
    if prev.endswith("-"):
        return prev[:-1] + nxt
    return prev + " " + nxt


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class RawOption:
    key: str
    text: str


@dataclass
class RawQuestion:
    id: str
    number: Optional[int]
    section: str
    category: str
    subcategory: str
    question: str
    options: List[RawOption] = field(default_factory=list)
    answer_type: str = "single"
    essential: bool = False
    image_required: bool = False
    src_page: int = 1
    region_note: Optional[str] = None
    line_no: int = 0
    triage_note: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "number": self.number,
            "section": self.section,
            "category": self.category,
            "subcategory": self.subcategory,
            "question": self.question,
            "options": [{"key": o.key, "text": o.text} for o in self.options],
            "answerType": self.answer_type,
            "essential": self.essential,
            "imageRef": None,
            "imageRequired": self.image_required,
            "srcFile": "cuestionario.pdf",
            "srcPage": self.src_page,
            "regionNote": self.region_note,
            "line_no": self.line_no,
            "triage_note": self.triage_note,
        }


# ---------------------------------------------------------------------------
# Question-block parser
# ---------------------------------------------------------------------------
_OPTION_CONT_MARKER = re.compile(r"^\s{3,}\S")


def _is_noise(s: str) -> bool:
    return bool(_NOISE_RE.match(s)) or bool(_HEADING_RE.match(s))


def _split_option(s: str):
    """Return (key, text) for an option line, or None if not an option."""
    m = _BULLET_VF_RE.match(s)
    if m:
        key = "v" if m.group(1).lower() == "verdadero" else "f"
        return key, m.group(1).capitalize()
    if _COLUMNAR_VF_RE.match(s):
        return None, None  # columnar grid signal; handled by caller
    m = _OPTION_RE.match(s)
    if m:
        return m.group(1).lower(), m.group(2).strip()
    return None


def _strip_stem_metadata(text: str):
    """Extract (clean_text, essential, region_note) from a stem line."""
    essential = bool(_ELIMINATORIO_RE.search(text))
    text = _ELIMINATORIO_RE.sub("", text)
    m = _REGION_RE.search(text)
    region = m.group(1) if m else None
    text = _REGION_RE.sub("", text)
    return text.strip(), essential, region


def _parse_section(lines: List[str], section: str, category: str) -> List[RawQuestion]:
    questions: List[RawQuestion] = []
    current: Optional[RawQuestion] = None
    current_page = 1
    seq = 0
    line_no_start = 1

    def flush():
        nonlocal current, seq
        if current is None:
            return
        # Columnar V/F: a grid observed right after the stem means truefalse
        # even though no bullet options are present (grid carries no text).
        if current.options and {"v", "f"} == {o.key for o in current.options}:
            current.answer_type = "truefalse"
        elif current.options:
            current.answer_type = "single"
        else:
            current.answer_type = "single"
            current.triage_note = "no options parsed"
        questions.append(current)
        current = None

    for idx, raw_line in enumerate(lines):
        line_no = line_no_start + idx
        s = clean_text(raw_line)
        stripped = s.strip()
        if not stripped:
            continue

        mfoot = _FOOTER_RE.search(s)
        if mfoot:
            current_page = int(mfoot.group(1)) + 1
            continue
        if _is_noise(s):
            continue

        mnum = _NUMBERED_RE.match(s)
        if mnum:
            if current is not None and (current.options or current.question):
                flush()
            seq += 1
            stem, essential, region = _strip_stem_metadata(mnum.group(2))
            current = RawQuestion(
                id=f"{section}-{seq:04d}",
                number=int(mnum.group(1)),
                section=section, category=category, subcategory=section,
                question=stem, essential=essential, src_page=current_page,
                region_note=region, line_no=line_no,
            )
            continue

        opt = _split_option(stripped)
        if opt is not None:
            if current is None:
                continue  # orphan option without a stem: pdftotext misplaced it
            if opt[0] is None:
                # columnar V/F marker: remember for answerType inference
                current.options.append(RawOption("v", "Verdadero"))
                current.options.append(RawOption("f", "Falso"))
                continue
            key, text = opt
            current.options.append(RawOption(key, text))
            continue

        if current is None:
            # new unnumbered question (section heading already filtered)
            seq += 1
            stem, essential, region = _strip_stem_metadata(stripped)
            current = RawQuestion(
                id=f"{section}-{seq:04d}", number=None,
                section=section, category=category, subcategory=section,
                question=stem, essential=essential, src_page=current_page,
                region_note=region, line_no=line_no,
            )
            continue

        if current.options:
            # A new non-option line after options: either an indented option
            # continuation, or the start of the next unnumbered question.
            if _OPTION_CONT_MARKER.match(s):
                nxt = stripped
                prev = current.options[-1].text
                current.options[-1].text = _join_wrapped(prev, nxt)
            else:
                flush()
                seq += 1
                stem, essential, region = _strip_stem_metadata(stripped)
                current = RawQuestion(
                    id=f"{section}-{seq:04d}", number=None,
                    section=section, category=category, subcategory=section,
                    question=stem, essential=essential, src_page=current_page,
                    region_note=region, line_no=line_no,
                )
            continue

        # else: continuation of the stem text
        current.question = (current.question + " " + stripped).strip()

    flush()

    for q in questions:
        q.image_required = bool(_IMAGE_STEM_RE.search(q.question))
    return questions


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def parse_battery_text(
    text: str,
    src_file: str = "cuestionario.txt",
    section_slug: str = "fixture",
    category: str = "generales",
    in_scope: bool = True,
) -> List[dict]:
    """Parse battery text into raw question dicts (no answers)."""
    if not in_scope:
        return []
    lines = text.split("\n")
    questions = _parse_section(lines, section_slug, category)
    return [q.to_dict() for q in questions]


def extract_full(input_txt: Path, section_map: Optional[List[tuple]] = None) -> dict:
    """Production extraction: split the full file by SECTION_MAP line ranges."""
    section_map = section_map or SECTION_MAP
    text = input_txt.read_text(encoding="utf-8")
    all_lines = text.split("\n")
    by_section: dict = {}
    for slug, category, in_scope, start, end in section_map:
        if not in_scope:
            continue
        chunk_lines = all_lines[start - 1 : end]
        questions = _parse_section(chunk_lines, slug, category)
        by_section[slug] = [q.to_dict() for q in questions]
    return by_section


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    input_txt = Path(argv[0]) if argv else (
        Path.home() / "AppData" / "Local" / "Temp" / "opencode" / "cuestionario.txt"
    )
    output_dir = Path(argv[1]) if len(argv) > 1 else Path("data/_extracted")
    output_dir.mkdir(parents=True, exist_ok=True)
    by_section = extract_full(input_txt)
    total = sum(len(v) for v in by_section.values())
    for slug, qs in by_section.items():
        (output_dir / f"{slug}.json").write_text(
            json.dumps(qs, ensure_ascii=False, indent=1), encoding="utf-8"
        )
    (output_dir / "manifest.json").write_text(
        json.dumps({"source": str(input_txt), "total": total,
                    "sections": {k: len(v) for k, v in by_section.items()}},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"extracted {total} questions across {len(by_section)} sections -> {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())