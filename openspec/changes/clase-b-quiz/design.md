# Design: Clase B Quiz App (Registro Marcos Paz)

## Technical Approach

Greenfield static app on a green repo (verified: only source PDFs + `openspec/` exist). Data-first: a Python build pipeline turns `cuestionario.txt` (`pdftotext` extraction) into schema-validated per-category JSON banks; a pure-JS quiz engine (ESM, no DOM) samples/shuffles/scores client-side; vanilla HTML/CSS/JS renders quiz, study, and material views using relative-path fetches that are subpath-safe for GitHub Pages. Strict TDD: pytest for the data/build layer, vitest for the JS engine, with a Python→Node parity test binding them.

## Architecture Decisions

| Decision | Options | Tradeoff | Choice |
|---|---|---|---|
| Bank granularity | 16 per-section files vs 3 per-category files + `index.json` | Spec wording says "per section"; exploration example shows category files; quiz strata and study filters are category-driven; 16 files = 16 lazy fetches of a ~2 MB total | **3 category files** — `generales.json`, `senales.json`, `auto.json` — plus `index.json` (section→category map, counts). Documented deviation: categories ARE the sampling strata |
| Engine implementation | Pure JS ESM (vitest) + Python mirror | Dual implementations drift; single JS impl leaves Python blind | **Single JS engine** (`quiz-engine.js`, pure functions, seedable RNG); pytest runs `node` on it over a fixture bank to assert invariants (parity test) |
| Confidence persistence | Inline `confidence`+`reviewed` per question vs separate overlay file | Inline ships authoring metadata to Pages (harmless, useful for "verificado" badge); overlay adds merge complexity | **Inline fields**; `scripts/confidence_report.py` derives `data/review-queue.json` (gitignored, regenerable) |
| Deploy | gh-pages branch vs Actions workflow | Branch publish is manual and drift-prone; Actions rebuilds from `main` | **GitHub Actions** publishing repo root; `.nojekyll`; all refs relative (`./data/...`) — subpath-safe |
| Module style | IIFE globals vs ESM | `file://` breaks ESM anyway; spec demands a friendly fetch-error state | **ESM** via single `<script type="module" src="./js/app.js">` |

## Data Flow

```
cuestionario.pdf ──pdftotext──► %TEMP%\opencode\cuestionario.txt
        │ (regenerable, gitignored)
        ▼
scripts/extract.py ──► scripts/build_bank.py ──► data/{generales,senales,auto}.json
  (mojibake fix, V/F grids,         │  (schema-validated; srcFile/srcPage)
   unnumbered ids, triage)          ▼
                           scripts/confidence_report.py ──► data/review-queue.json
        ▼
index.html ──./js/app.js──► data-loader (fetch ./data/index.json → lazy category files)
        ├─► quiz-engine.js (sample/shuffle/score) ──► quiz-view.js
        ├─► study-view.js
        └─► materials-view.js (./data/materials.json)
```

## File Changes

| File | Action | Description |
|---|---|---|
| `index.html` | Create | Single page, nav for quiz/study/materials; repo root = Pages root |
| `css/style.css` | Create | Plain CSS, no framework |
| `js/app.js`, `js/config.js` | Create | Bootstrap/router; single config point: `EXAM_SIZE=40`, `PASS_THRESHOLD=30`, floors `{senales:8, generales:20, auto:6}`, `CONFIDENCE_GATE=0.9` |
| `js/data-loader.js` | Create | Relative fetch + friendly error banner (404 or `file://`); app stays usable |
| `js/quiz-engine.js` | Create | Pure ESM: stratified sampling, essential include, Fisher–Yates + key remap, scoring |
| `js/quiz-view.js`, `js/study-view.js`, `js/materials-view.js` | Create | View renderers (feedback loop, filters, cards) |
| `data/index.json`, `data/{generales,senales,auto}.json`, `data/materials.json` | Create | Question bank (source of truth) + 5 material cards |
| `scripts/extract.py`, `scripts/build_bank.py`, `scripts/confidence_report.py` | Create | Build pipeline + review gate |
| `tests/` (pytest), `js/quiz-engine.test.js` (vitest) | Create | See Testing Strategy |
| `.github/workflows/deploy.yml`, `.nojekyll`, `.gitignore` | Create | Pages deploy, Jekyll bypass, derived-artifact ignores |
| `assets/signs/` | Create | Placeholder dir; image pipeline deferred |

## Interfaces / Contracts

Question object (final schema, per spec): `id {section}-{seq}`, `number` (nullable, dupes legal), `section` (16 slugs), `category: "generales"|"senales"|"especificas-auto"`, `subcategory`, `question`, `options[] {key,text}` (V/F normalized to `v`/`f`), `correct` (single key), `answerType: "single"|"truefalse"`, `fundamento`, `sources[] {material,ref,page}`, `essential` bool, `imageRef` (nullable), `imageRequired` bool, `srcFile`, `srcPage`, `regionNote` (nullable), `confidence` (0–1), `reviewed` bool.

`index.json`: `{version, generated, sections:{slug→{category,count}}, categories:{…counts}}`. `materials.json`: 5 × `{id,title,queEs,queEstudiar,peso}`; `peso` is rank 1–5 (Cuestionario = 1, highest).

Engine contract: `buildExam(bank, cfg, seed) → {questions:[{id, options:[{displayKey,text}], correctDisplayKey, …}], seatLog}` — deterministic under a seed.

### Sampling algorithm (stratified + essential force-include)

1. Candidate pool = bank minus `imageRequired` items.
2. **Essentials**: sort by `(confidence desc, number asc, id asc)`; include all if ≤ 40, else deterministic top-K. Essential inclusion takes precedence over the señales cap (cap yields).
3. Remaining seats `R = 40 − |E|`. Per category: `min_c = clamp(floor_c − |E_c|, 0, avail_c)`; draw `min_c` first; deficits from pools smaller than their floor are redistributed to other categories.
4. Allocate residual slots category-by-category without replacement, weighted by remaining pool size, never exceeding caps; guard: exactly 40 unique `id`s.
5. Per render: Fisher–Yates option shuffle; bijective `displayKey` remap; `correctDisplayKey = displayKey[correct]` — bank object never mutated.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Data | Schema integrity, `id` uniqueness, `correct ∈ options`, enums, V/F shape, imageRequired rules, duplicate `number` tolerated | `tests/test_schema.py` — jsonschema + assertions on real bank |
| Build | Mojibake cleaning, unnumbered `id` assignment, scope triage, review gate | `tests/test_build_pipeline.py` (golden fixtures from `cuestionario.txt` samples); `tests/test_review_queue.py` |
| Engine (JS) | 40 unique, no imageRequired, señales ≤ 8 / generales ≥ 20 / auto ≥ 6, essentials always present, cap-yield, floor-deficit reallocation, shuffle bijection + remap, threshold pass/fail | `js/quiz-engine.test.js` — vitest, seeded RNG |
| Parity | Python runs the JS engine over a fixture bank → same invariants | `tests/test_engine_parity.py` — `node` subprocess |
| UI (light) | Load-error state, lazy section fetch, empty filter state, 5 cards render | vitest + jsdom |

Apply phase MUST follow `strict-tdd.md` (tests written before implementation; red→green per task).

## Migration / Rollout

No migration (green repo). Rollout = authoring gate: deploy workflow fails while `data/review-queue.json` is non-empty; never publish unreviewed answers. Answer-key JSON is the irreplaceable artifact — extraction script regenerates structure, not answers.

## Open Questions

- [ ] Default `CONFIDENCE_GATE` value (0.9 proposed) — confirm at authoring kickoff.
- [ ] Final Pages repo name assumed `registro-conducir-buenos-aires`; relative paths make this moot regardless.
