# Exploration: Clase B Driving Exam Study Web App (Marcos Paz, Buenos Aires)

## Current State

The repo `registro-marcos-paz` is a static site + JSON question bank for preparing the theoretical driving exam (Clase B / auto) in Marcos Paz, Buenos Aires. The exam: ~40 multiple-choice questions, pass threshold ~30/40 (75%). All source material is in the working dir in PDF/DOCX form:

- `cuestionario.pdf` — official provincial battery (228 pages, IF-2019-33101289-GDEBA-DPPYSVMGGP), **no answer key**
- `manualdelconductor actualizado.docx` — official driver manual (845 extracted lines; "Versión resumida" of the PBA Manual del Conductor, Morón/DIEBO 2008 + ANSV)
- `ansv_licencias_libro_senales_de_transito - copia - copia.pdf` — ANSV traffic signs book (26 pages, **image-only PDF, no text layer**)
- `LEY 24449 ACTUALIZADA.pdf` — national traffic law (3590 extracted lines)
- `Ley_13927_1 (2).pdf` — province adherence law / traffic code (816 lines)

A text extraction of the battery already exists at `%TEMP%\opencode\cuestionario.txt` (10215 lines, `pdftotext -layout`). It was verified present and re-analyzed in full.

## Battery Structure (cuestionario.txt)

### Numbering scheme (IMPORTANT — has quirks)

- The battery numbers questions **globally 1..548** across the ENTIRE document (not restarting per section), but:
  - **Unnumbered blocks exist**: preamble "actores en la via publica" (~59 q), sections 1-3 (Seguridad/Documentación/intoxicación — questions unnumbered in text layer), the image block at the start of Señales (~50 q), and section 13 "Conducción segura" (~151 q). These are numbered blocks whose numbers were NOT captured by pdftotext, OR genuinely unnumbered source questions.
  - **538 numbered matches** found (both `NNN)` and attached `NNN)texto` formats), max number 548.
  - **13 missing numbers** in 1..548: 34, 193, 324, 371, 412-420 (mostly in out-of-scope "transporte de cargas" section).
  - **Duplicated numbers** (same number, different question): 82, 139, 225, 349 — these are image-question pairs (e.g. two different signals both numbered 225).
- **Section headings** use their own numbering `1)..13)` for general, `1)..9)` for class-specific — collides with question numbers in the same regex but they are distinguishable by text.

### Section map with line ranges (cuestionario.txt)

| # | Section | Lines | Numbered? | Est. questions | Clase B scope |
|---|---------|-------|-----------|----------------|---------------|
| — | PREGUNTAS GENERALES title | 31 | — | — | — |
| 0 | actores en la via publica (preamble) | 34–666 | no | ~59 | ✅ IN |
| 1 | Seguridad | 667–849 | no | ~24 | ✅ IN |
| 2 | Documentación | 850–1055 | no | ~23 | ✅ IN |
| 3 | intoxicación y alcohol | 1056–1484 | no | ~45 | ✅ IN |
| 4 | varias | 1485–2248 | yes 1–79 | ~65 | ✅ IN |
| 5 | Semáforo | 2249–2368 | yes 80–91 | ~14 | ✅ IN |
| 6 | Velocidades | 2369–2661 | yes 92–121 | ~31 | ✅ IN |
| 7 | Adelantamiento | 2662–2794 | yes 122–132 | ~16 | ✅ IN |
| 8 | Autopistas | 2795–2925 | yes 133–143 | ~12 | ✅ IN |
| — | Tracción a Sangre | 2926–2991 | yes 144–148 | ~11 | ❌ OUT (not Clase B; horses/animals) |
| 9 | Estacionamiento | 2992–3092 | yes 149–157 | ~11 | ✅ IN |
| 10 | Luces | 3093–3221 | yes 158–169 | ~15 | ✅ IN |
| 11 | Giros y rotondas | 3222–3375 | yes 170–183 | ~20 | ✅ IN |
| 12 | Señales de Tránsito | 3376–4608 | partial: img block (un-numbered ~50) + 184–239 | ~108 | ✅ IN (image-heavy) |
| 13 | Conducción segura | 4609–6398 | no | ~151 | ✅ IN |
| 14 | Seguridad Activa y Pasiva | 6399–6486 | yes 540–548 | ~9 | ✅ IN (note: in battery numbering this is the tail 540+) |
| — | PREGUNTAS ESPECÍFICAS SEGÚN CLASE | 6487–6488 | — | — | — |
| 1) | Auto y Camioneta | 6489–7398 | yes 240–279 + unnumbered block | ~86 | ✅ IN (CORE for Clase B) |
| 2) | Camionetas y vehículos de carga | 7399–7655 | yes 280–304 | ~28 | ❌ OUT (Clase C) |
| 3) | Motos | 7656–8185 | yes 305–338 | ~56 | ❌ OUT (Clase A) |
| 4) | Servicios de urgencia/emergencia | 8186–8469 | yes 339–363 | ~32 | ❌ OUT |
| 5) | Taxis y Remises | 8470–8623 | yes 364–379 | ~20 | ❌ OUT |
| 6) | Vehículos transporte de cargas | 8624–9362 | yes 380–458 | ~52 | ❌ OUT |
| 7) | Camión sin Acoplado / Casas Rodantes | 9363–9568 | yes 459–478 | ~17 | ❌ OUT |
| 8) | Camiones con acoplado | 9569–9925 | yes 479–514 | ~22 | ❌ OUT |
| 9) | >8 pasajeros | 9926–10180 | yes 515–539 | ~17 | ❌ OUT |
| — | Signature page | 10181–10215 | — | — | — |

### In-scope estimate for Clase B (auto)

Sum of IN-scope est. questions (pragmatic, ±15%):
- General sections (preamble + 1..14): ~59+24+23+45+65+14+31+16+12+11+15+20+108+151+9 ≈ **~603**
- Auto y Camioneta (specific 1): ~86 (numbered 240–279 = 40 + unnumbered block ~38–48 + eliminatorio variants)
- **Total in-scope ≈ 680–690 questions** (of ~944 total across the whole battery)

Out-of-scope sections (moto, tracción a sangre, transporte escolar/pasajeros, cargas/maquinaria, urgencia/emergencia, taxis, camiones) ≈ 250+ questions — excluded because Clase B = automóvil/camioneta particular.

### Missing numbers noted (in 1..548)
34, 193, 324, 371, 412–420 — mostly extraction gaps in image-heavy or out-of-scope sections. Not blockers; data model must tolerate gaps.

### Answer format variants

- `A. / B. / C.` uppercase-dot (596 lines) — most common
- `A) / B) / C)` uppercase-paren (328)
- `a) / b) / c)` lowercase-paren (596) — also multi-option up to f)
- `A – B – C` dash style (10)
- `• Verdadero / • Falso` bullet V-F
- Columnar `V  F` (121) — true/false answer grids
- "Verdadero/Falso" text lines (79 each)
- Special markers: "(Pregunta de carácter eliminatorio)" — seen ~50× in-scope; "(Bahia Blanca)" city variants (~14×) — flag as source/region notes, still usable

### Image-dependent questions

- The Señales section opens with a **large image block (lines 3377–3940, ~50 questions)** where each question is a signal image + question text ("La siguiente señal indica:", "¿Cuál de las siguientes imágenes...?", "Figura A/B/C"). The text layer contains the question stem + options but NOT the images.
- ~21 explicit image-stem matches across the whole file ("La siguiente imagen corresponde a:", "visualiza en la imagen", "Figura A."), plus every "La siguiente señal indica:" in the numbered Señales block (~30 of the 55 numbered Señales questions are image-referencing).
- Estimate: **~60–80 image-dependent questions total**, concentrated in Señales (section 12) and a few in preamble/auto/conducción.

**Handling in data model**: `imageRef` field + a companion strategy — either (a) crop images from `cuestionario.pdf` pages during build (pdftoppm per page + manual mapping), or (b) mark `"imageRequired": true` and render a placeholder, or (c) for study purposes re-derive visual questions as text-only reframing. Recommend (a) as an enhancement phase; data model prepares for it from day one.

## Material Summaries (proposed summary cards for the web app)

1. **Cuestionario oficial (Batería de preguntas)** — the 550-question battery itself; the primary question source. Study the whole in-scope set; questions repeat 1:1 in the real exam with high probability. Weight: highest (the exam pulls from this battery).
2. **Manual del Conductor (PBA/ANSV resumido)** — chapters: I Educación ética y ciudadana; II La conducción (modalidades, circulación, velocidad); III Conozca su vehículo (función, seguridad); IV La vía pública (uso, señales básicas); V Condiciones psicofísicas del conductor; VI Señales viales; VII Licencia Nacional de Conducir. Use for `fundamento`/explanations and concepts. Weight: medium-high (question fundamentals).
3. **Libro de Señales de Tránsito (ANSV)** — 26-page visual catalog of all regulatory/preventive/informative signs. Image-only PDF → must be captured as images. Use as the image source for all `imageRef` sign questions (better than cropping the battery). Weight: medium (sign questions are image-based; exam includes them).
4. **Ley Nacional de Tránsito 24.449** — national traffic law; source for legal-article citations in `fundamento` (e.g. prioridad de paso, velocidades, documentación). Weight: low-medium (used for justification, not memorized directly).
5. **Ley Provincial 13.927** — province adherence to national law + province-level rules (Marcos Paz jurisdiction). Weight: low (context; a few questions reference province-specific items).

## Data Model (proposed JSON schema)

```jsonc
{
  // One question object (one entry per question)
  "id": "gen-04-014",                    // stable slug: {section-slug}-{seq}, e.g. "senales-023", "auto-240"
  "number": 225,                          // number in the official battery (nullable if unnumbered block); duplicates allowed (image pairs) — use id for uniqueness
  "section": "senales",                  // section slug (see section map): preambulo, seguridad, documentacion, intoxicacion, varias, semaforo, velocidades, adelantamiento, autopistas, estacionamiento, luces, giros, senales, conduccion, seg-activa, auto
  "category": "generales",               // "generales" | "senales" | "especificas-auto"
  "subcategory": "señales reglamentarias", // free-ish taxonomy per section, e.g. "semáforos", "prioridad de paso", "velocidades", "documentación"
  "question": "La siguiente señal indica:", // question text (may be incomplete without image)
  "options": [
    { "key": "a", "text": "Detención transporte público." },
    { "key": "b", "text": "Terminal ómnibus" },
    { "key": "c", "text": "Punto panorámico" }
  ],
  // V/F questions: options become [{key:"v", text:"Verdadero"},{key:"f", text:"Falso"}]
  "correct": "b",                         // single key; for V/F: "v" or "f"
  "answerType": "single",                 // "single" | "truefalse" (future: "multiple")
  "fundamento": "…",                      // explanation written by us (from manual/law/battery reasoning)
  "sources": [
    { "material": "manual", "ref": "Cap VI — Señales viales", "page": null },
    { "material": "ley-24449", "ref": "art. 77, inc. a)", "page": null },
    { "material": "ansv-senales", "ref": "pág. 12", "page": 12 },
    { "material": "cuestionario", "ref": "pág. 96", "page": 96 }
  ],
  "essential": true,                      // "sí o sí" — eliminatorio flag in battery; force-include in exams
  "imageRef": "assets/signs/rotonda-01.png", // null if text-only question
  "imageRequired": true,                  // true if stem is meaningless without the image
  "srcFile": "cuestionario.pdf",
  "srcPage": 96,                          // PDF page where question lives (extraction page footer gives exact page)
  "regionNote": "Bahia Blanca"            // optional quirks (city-variant question) — nullable
}
```

Notes:
- `id` is the uniqueness key (battery duplicates like 225x2 are legal).
- `correct` is **the big build task**: the battery has NO answer key — each `correct` + `fundamento` must be derived from manual/law/ANSV + domain reasoning. Flag low-confidence answers (`confidence: 0.6` in a hidden build field or review queue).
- Store as one JSON file per section (`data/generales.json`, `data/senales.json`, `data/auto.json` + `data/index.json`) for static hosting and lazy loading.

## Quiz Mechanics (design input)

- **Exam = 40 questions**, stratified random sampling: choose N per category proportional to category size, with floors: e.g. señales ≤ 8, generales ≥ 20, auto ≥ 6 → guarantees NOT all-from-señales. Implement: sample `k_i = clamp(round(40 * size_i / total), floor_i, ceil_i)` then adjust residuals randomly.
- **Force-include essentials**: all questions flagged `essential: true` (≈50 eliminatorio in scope) are candidates; pick the critical subset (e.g. 5–8) deterministically each exam to guarantee "sí o sí" coverage, then fill the rest stratified.
- **No repeats across exam**: sample without replacement within a single exam; shuffle option key order per render (options presented in random order, `correct` key remapped).
- **After-answer feedback (mandatory)**: show immediately after each answer — correct/incorrect + `fundamento` + `sources[]` chips (manual cap / law art / ANSV page), regardless of correctness. This is the study loop; no "skip feedback" mode.
- Scoring: 1 pt/question, pass ≥ 30/40 (75%), show progress bar.

## Risks & Unknowns

1. **No answer key in the battery** — the entire `correct` + `fundamento` dataset must be authored from manual+law+reasoning. High manual effort; risk of wrong answers → needs a review pass (second-person check or cross-validation across the 4 sources). HIGH.
2. **Image questions (~60–80)** — cannot be captured from text layer; ANSV book is image-only. Requires image pipeline (pdftoppm crops) and sign→question mapping. Medium-High.
3. **Numbering quirks** — global numbering with 13 gaps, 4 duplicate numbers, and unnumbered blocks; safe only if `id` (not `number`) is the join key.
4. **Category classification errors** — Clase B scope is judgment-based (e.g. "Camionetas y carga" excluded; some general questions are moto-flavored like 545–547 "partes de una motocicleta" buried in Seguridad Activa section). Budget a manual triage pass.
5. **OCR/extraction artifacts** — mojibake accents (Ã© etc.), line-wrapped options, "V F" columnar grids may split options; JSON build needs text cleaning + re-joining.
6. **"Eliminatorio" semantics** — battery marks some "(Pregunta de carácter eliminatorio)"; real exam behavior in Marcos Paz is unverified — treat as "essential study" not literal exam mechanic.
7. **Pass threshold uncertainty** — 30/40 (75%) is "per most sources"; the app should make threshold configurable.
8. **Ley 24.449 vs 13.927 interplay** — some questions reference decree-level regs; make sure fundamentos cite the right law.

## Ready for Proposal
Yes. Recommend the orchestrator tell the user: exploration complete — ~680 in-scope questions mapped, data model + quiz mechanics defined, main cost is authoring the answer key/fundamentos, image pipeline is the only external dependency.