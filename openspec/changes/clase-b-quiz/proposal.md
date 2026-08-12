# Proposal: Clase B Quiz App (Registro Marcos Paz)

## Intent

User failed the Clase B theoretical driving exam twice in Marcos Paz (Buenos Aires). Needs efficient study over the official battery (~680 in-scope Clase B questions of ~944 total). The battery has NO answer key — correct answers + `fundamento` must be authored from manual + laws + ANSV + reasoning (main cost, HIGH risk of error). The app must run on GitHub Pages with no backend.

## Scope

### In Scope
- JSON question bank (source of truth), schema per exploration: one file per section + `data/index.json`; generated from `cuestionario.pdf` text extraction (`%TEMP%\opencode\cuestionario.txt`)
- Answer-key authoring: `correct`, `fundamento`, `sources[]` per question; `confidence` flag + review queue for low-confidence answers
- Quiz mode: 40-question simulated exam, stratified random sampling (señales ≤ 8, generales ≥ 20, auto ≥ 6), force-include essential ("eliminatorio") subset, no repeats per exam, shuffled option order, feedback after EVERY answer
- Study mode: browse/filter by category; answer + fundamento + sources
- Material summary cards (5 materials: cuestionario, manual, señales ANSV, Ley 24.449, Ley 13.927)
- Static HTML/CSS/JS app, deployable to GitHub Pages

### Out of Scope
- Non-Clase B sections (moto, carga, escolar, taxis, emergencia, tracción a sangre, camiones)
- Image pipeline (pdftoppm crops from PDFs) — deferred enhancement phase
- Backend/auth, multiple-answer questions, verification of "eliminatorio" as a real exam mechanic

**Image questions (~60–80, concentrated in Señales):** included in data model + study mode now via `imageRef` placeholder + link to the source PDF page (`srcPage`); EXCLUDED from quiz sampling while `imageRequired: true`, flipped on when the image pipeline lands.

## Capabilities

> No existing specs under `openspec/specs/` — all capabilities are new.

### New Capabilities
- `question-bank`: JSON schema, extraction/build pipeline, answer-key authoring + review queue
- `quiz-mode`: stratified 40-q sampling, essential force-include, mandatory feedback loop
- `study-mode`: category browsing with answer + fundamento + sources
- `material-summaries`: 5 summary cards (1 per study material)
- `static-site`: HTML/CSS/JS app + GitHub Pages deployment

### Modified Capabilities
None.

## Approach

Data-first: extraction script + manual authoring produce `data/*.json`. `id` (not battery `number`) is the join key — duplicates (e.g. 225x2 image pairs) and numbering gaps are legal. V/F questions normalized to two options. Low-confidence answers flagged for review. Quiz engine samples per floor/ceil strategy, filters `imageRequired`, remaps shuffled option keys at render. Static app fetches JSON and renders mandatory after-answer feedback. Deploy via GitHub Pages.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `data/*.json` + `data/index.json` | New | Per-section question bank (source of truth) |
| `scripts/` | New | Extraction + build + confidence report |
| `index.html`, `css/`, `js/` | New | Static quiz/study app |
| `assets/signs/` | New (placeholder) | Future sign images from ANSV book |

## Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| No answer key → authoring effort, wrong answers | High | `confidence` flag; second-person review pass before launch |
| ~60–80 image questions | Med-High | Excluded from quiz until pipeline; placeholder + source-page link |
| Numbering/extraction quirks (gaps, dupes, mojibake) | Med | `id`-based joins; text cleaning pass |
| Clase B scope misclassification | Med | Manual triage pass (moto-flavored Qs buried in general sections) |
| "Eliminatorio" semantics unverified | Low | Treat as study-essential; pass threshold configurable |

## Rollback Plan

All content is static and git-tracked: revert commit/branch, drop gh-pages release. No data migration. Answer-key JSON is irreplaceable — never merge unreviewed answers; extraction script allows regeneration from source PDFs.

## Dependencies

- Source materials in working dir: `cuestionario.pdf`, `manualdelconductor actualizado.docx`, `ansv_licencias_libro_senales_de_transito.pdf`, `LEY 24449 ACTUALIZADA.pdf`, `Ley_13927_1 (2).pdf`
- (future) poppler `pdftoppm` for the image pipeline

## Success Criteria

- [ ] 40-question quiz runs entirely from `data/*.json` (no hardcoded questions)
- [ ] Every answer shows correct/incorrect + `fundamento` + `sources[]` chips
- [ ] Every exam: señales ≤ 8, generales ≥ 20, essential questions included, no repeats
- [ ] Study mode filters by category; all 5 material cards render
- [ ] App loads correctly on GitHub Pages URL