# Design: Study Summaries (Resúmenes)

## Technical Approach

Data-first, additive change on the existing static app: a hand-authored `data/resumenes.json` (5 entries, `ideasClave` bullets per material, `licencias` tags) consumed by a new `resumenesView` that mirrors studyView's filter + empty-state pattern and materialsView's card rendering. A single `<select>` is built at render time from the union of `licencias` values — never hardcoded — so a future `moto` tag appears with zero code changes. No pipeline, no backend; `js/app.js` gains a nav entry + route, and `index.html` is untouched (nav auto-renders from `VIEW_NAMES`).

## Architecture Decisions

| Decision | Options | Tradeoff | Choice |
|---|---|---|---|
| Summary field name | `resumen` vs `ideasClave` | Proposal used `resumen`, spec used `ideasClave`; `resumen` undersells cheat-sheet bullets and drifts from spec | **`ideasClave`** (resolved) — non-empty array of short key-idea strings |
| Bullet shape | Plain string vs `{text, ref}` object | Objects enable ref chips later but add renderer + schema weight; refs here are for human review traceability, not UI interaction | **Plain strings**, ref inline in the bullet ("— art. 41, Ley 24.449"); `{text, ref}` remains a non-breaking future extension |
| Nav label mechanism | Raw name `resumenes` vs minimal label map | Raw name fails the spec's visible "Resumenes" link; renaming ALL nav links is scope creep | **`NAV_LABELS` map** in app.js: `{ resumenes: 'Resumenes' }`, fallback to raw name — existing quiz/study/materials links unchanged (documented cosmetic inconsistency) |
| License filter | Hardcoded options vs derived at render | Hardcoded breaks on new tags | **Derived** — `[...new Set(entries.flatMap(e => e.licencias))]`, "Todas" (`value=""`) default (resolved) |
| Authoring guardrail | Per-bullet flags vs per-entry vs new pipeline | Per-bullet is heavier than needed; a pipeline contradicts "data-only" | **Per-entry `confidence` (0–1) + `reviewed` (bool)**, inline like bank questions; human review flips `reviewed:true` before merge — no new pipeline (resolved) |
| Data file shape | Wrapper object vs plain array | Spec mandates an array; matches materials.json | **Plain array**, 5 entries, materials.json simplicity |

## Data Flow

```
data/resumenes.json (hand-authored, 5 entries)
        │  dataUrl('resumenes.json')
        ▼
resumenesView.load() ──► resumenesView.render(content, entries)
        │  filter select: "Todas" + union(licencias) at render time
        ▼
resumen-card [ title · license chips · <ul> ideasClave bullets ]
        │  no entry matches the selected tag
        ▼
.empty-state ("No hay resúmenes para esa licencia.")
```

## File Changes

| File | Action | Description |
|---|---|---|
| `data/resumenes.json` | Create | 5 hand-authored entries, ids mirror materials.json |
| `js/views.js` | Modify | `resumenesView` appended after `materialsView` (file end) |
| `js/app.js` | Modify | `VIEW_NAMES` += `resumenes`; `NAV_LABELS` map; boot views registry entry |
| `js/views.test.js` | Modify | `resumenesView` describe (fake-data render) + data-shape describe (real file via fs) |
| `js/app.test.js` | Modify | Nav assertions: 4 links, "Resumenes" label, `#resumenes` route |
| `css/style.css` | Modify | `.resumen-card`, `.resumen-list`, `.ideas-clave`; `.license-chip` shares the `.source-chip` rule |

## Interfaces / Contracts

`resumenes.json` — array of entries (example):

```json
{
  "id": "cuestionario",
  "title": "Cuestionario oficial",
  "licencias": ["auto"],
  "confidence": 0.95,
  "reviewed": false,
  "ideasClave": [
    "Prioridad en puente angosto: el que circula por la derecha (art. 41, Ley 24.449).",
    "Ante ambulancia con sirena: ceder el paso (art. 64, Ley 24.449)."
  ]
}
```

All 5 ids: `cuestionario`, `manual`, `ansv-senales`, `ley-24449`, `ley-13927`; initial `licencias: ["auto"]`. View contract `{ load(), render(content, data) }` identical to siblings; `load: () => loadJSON(dataUrl('resumenes.json'))`. Bullets: ≤ ~15 words, one key idea each, source ref (art./cap./sección) inline where feasible.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Data shape | 5 entries, exact ids, non-empty `ideasClave`/`licencias`, `confidence` ∈ [0,1], `reviewed` bool | `views.test.js` describe reading `data/resumenes.json` via `readFileSync` (index.test.js pattern) |
| View render | Cards: title, license chips, `ideasClave` bullets | `views.test.js` — inject fixture to `render(content, data)` (materialsView fake pattern) |
| Filter derivation | "Todas" + exactly "auto"; fixture entry `licencias:["moto"]` yields a "moto" option, no code change | Same describe, fixture-driven |
| Filter narrowing + empty state | Selected tag shows only matching cards; unmatched tag shows `.empty-state` | Dispatch `change` on the select (studyView empty-state pattern) |
| Nav / route | 4 nav ids; link label "Resumenes"; `#resumenes` renders the view | `app.test.js` — boot with 4 fake views; update every exact `navIds()` assertion |

## Migration / Rollout

No migration; static, additive, independently reversible (drop the nav entry to remove the section). Authoring gate = human review: content merged only with `reviewed: true`; no CI/deploy changes. Rollback: revert commit; remove `'resumenes'` from `VIEW_NAMES`.

## Open Questions

None blocking — field name, nav label, filter, bullet shape, and authoring guardrail resolved above. Note: the spec text accents the nav link ("Resúmenes"); the resolved label is "Resumenes" — tests assert the resolved value; reverting the accent is a one-character change if reviewers prefer it.