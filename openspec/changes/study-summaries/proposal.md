# Proposal: Study Summaries (Resúmenes)

## Intent

Learners need concise, exam-focused cheat-sheet summaries of each study material (cuestionario, manual, señales ANSV, Ley 24.449, Ley 13.927). The existing `material-summaries` cards only orient ("qué es / qué estudiar") — they don't distill key ideas; that knowledge lives only inside the source PDFs/docx, which are heavy to re-read. This change adds a "Resúmenes" study section: hand-authored key-idea bullets per material, tagged with the license classes they apply to, plus a DATA-DRIVEN license filter so future tags (e.g. `moto`) appear automatically with zero code changes.

## Scope

### In Scope
- `data/resumenes.json`, hand-authored from the 5 source files in repo root (answer-key authoring discipline): per material, concise key-idea bullets; schema supports MULTIPLE license tags; initial tags `["auto"]`
- `resumenesView` in `js/views.js` (studyView/materialsView pattern: `{ load(), render(content, data) }`), data via `dataUrl('resumenes.json')`
- License filter `<select>` built from the data (union of `licencias` across entries), "todas" default + empty state; route `#resumenes` + `VIEW_NAMES` entry (nav auto-renders from it in app.js), nav label "Resúmenes"
- Minimal CSS for filter + summary cards
- Vitest coverage: `resumenes.json` data shape, view behavior, license filtering

### Out of Scope
- Authoring for other license classes (`moto`, etc.) — schema supports it, content deferred
- Image pipeline, backend, PDF extraction/regeneration tooling

## Capabilities

### New Capabilities
- `study-summaries`: data-driven, license-tagged key-idea summaries per study material + license filter view

### Modified Capabilities
None — `material-summaries` (5 orientation cards) stays unchanged and is the baseline pattern this capability extends.

## Approach

Data-first, mirroring the bank: hand-author `data/resumenes.json` (`{id, title, licencias: [...], resumen: [bullets]}`, each bullet ≤ ~15 words, cheat-sheet not digest), deriving bullets from each PDF/docx. Filter options = union of all `licencias`, recomputed at render (no hardcoded tags), so adding `"licencias": ["moto", ...]` works untouched. `resumenesView` reuses studyView's filter + empty-state pattern. Bullets reference material id + ref (page/chapter) for traceability, like source chips.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `data/resumenes.json` | New | Hand-authored summaries with `licencias` tags |
| `js/views.js` | Modified | `resumenesView` added to registry |
| `js/app.js` | Modified | `VIEW_NAMES` += `resumenes` (nav + routing) |
| `js/views.test.js` | Modified | resumenesView + data-shape cases |
| `css/style.css` | Modified | Minimal filter/card styles |

## Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Hand-authored bullets misstate sources | Med | Ground each bullet to material + ref; human review pass before merge |
| Future license tag with no authored content → empty view | Med | "todas" default + empty-state copy (study-mode pattern) |
| Authoring volume across 5 materials | Med | Schema validated first; work-unit commits; enrich incrementally |

## Rollback Plan

Static + git-tracked: revert the commit/branch; drop `'resumenes'` from `VIEW_NAMES` to remove nav + route. No data migration; `resumenes.json` is additive and independent of the question bank.

## Dependencies

- `clase-b-quiz` change (complete) — conventions: views registry, `dataUrl` loader, vitest setup
- Source materials in repo root: `cuestionario.pdf`, `ansv_licencias_libro_senales_de_transito - copia - copia.pdf`, `LEY 24449 ACTUALIZADA.pdf`, `Ley_13927_1 (2).pdf`, `manualdelconductor actualizado.docx`

## Success Criteria

- [ ] `data/resumenes.json` schema-validated: one entry per material, non-empty `licencias` and `resumen`
- [ ] License filter options come from the data — adding a new `licencia` value requires zero code changes
- [ ] `#resumenes` route + "Resúmenes" nav link render; filter narrows summaries; empty state on no match
- [ ] Vitest suite (new + existing) green