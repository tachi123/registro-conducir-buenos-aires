# Tasks: Study Summaries (Resúmenes)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~400–550 (code + tests ≈ 300–380; `data/resumenes.json` ≈ 100–180) |
| 400-line budget risk | Medium |
| Chained PRs recommended | No |
| Suggested split | Single PR + size:exception (default); promotable: PR1 data + shape tests (~150) → PR2 authoring resumenes.json (~180) → PR3 resumenesView + tests (~200) → PR4 app nav + tests (~80) → PR5 CSS + README (~60) |
| Delivery strategy | single-pr-default |
| Chain strategy | size-exception |

```
Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Medium
```

### size:exception decision (recorded)
Cached session decision (maintainer pre-approved: "decidilo vos sin interaccion"; precedent: clase-b-quiz shipped ONE PR with size:exception). Every code slice is <400 lines; the over-budget driver is hand-authored authoring data (5 materials × ~8–12 bullets + inline refs), which is irreplaceable answer content, not reviewable code density. **Decision**: ONE PR with size:exception, work-unit commits (tests+code together); pre-granted.

### Work Units
| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Data schema + shape tests | PR 1 (single) | new data-shape describe reads real `data/resumenes.json` via readFileSync |
| 2 | Author `data/resumenes.json` | PR 1 | size:exception slice; commit per material pair with its bullets |
| 3 | resumenesView + view tests | PR 1 | fixture-driven render, filter, empty state |
| 4 | NAV_LABELS + VIEW_NAMES + app tests | PR 1 | update every 3-link `navIds()` assertion to 4 |
| 5 | CSS + README update | PR 1 | cosmetic slice, kept with the feature |

## Phase 1: Data + Schema
- [ ] 1.1 `js/views.test.js` data-shape describe (RED): `readFileSync` of `data/resumenes.json`; exactly 5 entries with ids `cuestionario`/`manual`/`ansv-senales`/`ley-24449`/`ley-13927`; each entry non-empty `ideasClave` and `licencias`; multi-tag entry validates; `confidence` ∈ [0,1], `reviewed` boolean.
- [ ] 1.2 Create `data/resumenes.json` skeleton: 5 entries, exact ids, `licencias: ["auto"]`, `confidence`/`reviewed` fields present (GREEN).
- [ ] 1.3 Author `cuestionario` bullets from `cuestionario.pdf` (prioridad, ambulancia, velocidad, VTV), inline refs (art., Ley 24.449), ≤15 words each.
- [ ] 1.4 Author `manual` bullets from `manualdelconductor actualizado.docx`, refs per Capítulo.
- [ ] 1.5 Author `ansv-senales` bullets from `ansv_licencias_libro_senales_de_transito - copia - copia.pdf`, refs per tipo/señal.
- [ ] 1.6 Author `ley-24449` bullets from `LEY 24449 ACTUALIZADA.pdf`, refs arts. 41, 42, 44, 47, 48, 49, 51, 64.
- [ ] 1.7 Author `ley-13927` bullets from `Ley_13927_1 (2).pdf`; set `reviewed: true` on all entries only after reading each source (human review gate; no CI change).

## Phase 2: resumenesView
- [ ] 2.1 Render test (RED): fixture entries → card per entry with title, license chips, `ideasClave` bullet list.
- [ ] 2.2 Implement `resumenesView` in `js/views.js` (append after `materialsView`): `{ load: () => loadJSON(dataUrl('resumenes.json')), render(content, entries) }` with `.resumen-card` + chips + `<ul class="ideas-clave">`.
- [ ] 2.3 Filter-derivation test (RED): options = "Todas" + union of `licencias`; fixture with `licencias: ["moto"]` yields a "moto" option with zero code edits.
- [ ] 2.4 Narrowing + empty-state tests (RED): dispatch `change` on the select → only matching cards; unmatched tag → `.empty-state`.
- [ ] 2.5 Implement filter in render: `<select>` built at render time from `[...new Set(entries.flatMap(e => e.licencias))]`, "Todas" (`value=""`) default; change narrows; no match → `.empty-state` "No hay resúmenes para esa licencia."

## Phase 3: Nav + Router
- [ ] 3.1 `js/app.test.js` (RED): every `navIds()` assertion expects 4 links (`nav-resumenes` last); boot with 4 fake views; assert nav label "Resumenes" via NAV_LABELS and `#resumenes` renders the view.
- [ ] 3.2 `js/app.js`: `VIEW_NAMES` += `'resumenes'`; add `NAV_LABELS` map `{ resumenes: 'Resumenes' }` with raw-name fallback (existing links unchanged); boot views registry += `resumenesView`; no `index.html` changes (nav auto-renders).

## Phase 4: Styling + Docs
- [ ] 4.1 `css/style.css`: `.resumen-card` (shares `.material-card` rule at line 67), `.ideas-clave` list, `.license-chip` sharing the `.source-chip` rule (line 115), filter spacing.
- [ ] 4.2 `README.md`: add Resúmenes section only if README already enumerates app sections (keep docs with the feature they explain).
- [ ] 4.3 `npm test` green (new + existing suite); browser smoke check: nav link, `#resumenes` cards, filter narrowing, empty state.