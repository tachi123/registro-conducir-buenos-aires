# Tasks: Clase B Quiz (static quiz app + JSON bank, GitHub Pages)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 12,500–20,000 (code ≈ 2,600; bank JSON ≈ 10,000–17,000) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | Single PR + size:exception (default); promotable: PR1 pipeline+engine (~1.3k) → PR2 site+deploy (~1.1k) → PR3–5 data (3–6k) |
| Delivery strategy | single-pr-default |
| Chain strategy | size-exception |

```
Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: size-exception
400-line budget risk: High
```

### size:exception decision (recorded)
Maintainer pre-approved ("tomes las mejores decisiones sin dudas"); ~80% of forecast is authored bank JSON (~680 questions; answer keys irreplaceable); code slices <400 lines. **Decision**: ONE PR with size:exception, work-unit commits (tests+code); pre-granted.

### Work Units
| Unit | Goal | Notes |
|------|------|-------|
| 1 | Scaffold tooling | pytest+vitest boot |
| 2 | Schema + fixtures + tests | question.schema.json, materials |
| 3 | extract.py + golden-fixture tests | mojibake, ids, srcPage |
| 4 | build_bank.py + tests | 3 category files + index.json |
| 5 | confidence_report.py + tests | review queue |
| 6 | Author data/*.json | size:exception slice |
| 7 | quiz-engine.js + vitest | sampling/floors/essentials/shuffle/threshold |
| 8 | test_engine_parity.py | node parity |
| 9 | config.js + data-loader.js + app.js + jsdom | fetch-error, lazy load |
| 10 | Views (quiz/study/materials) + jsdom | feedback, empty filter, cards |
| 11 | index.html + css/style.css | relative refs |
| 12 | Deploy workflow + .nojekyll + README | review gate |

## Phase 1: Foundation
- [ ] 1.1 Scaffold `.gitignore`, `package.json` (vitest+jsdom), `requirements.txt` (pytest, pytest-cov, jsonschema), `vitest.config.js`; pytest collects, vitest boots.
- [ ] 1.2 `data/schema/question.schema.json` + `tests/fixtures/bank-sample.json` + `tests/test_schema.py` + `tests/test_materials.py` (RED→GREEN): id unique, `correct∈options`, enums, V/F shape, imageRequired rules, dup numbers ok; 5 cards/4 fields, cuestionario peso 1.

## Phase 2: Build Pipeline + Data
- [x] 2.1 `scripts/extract.py` + `tests/test_build_pipeline.py` (golden fixtures from `cuestionario.txt`): mojibake, V/F grids, unnumbered ids, `srcPage`.
- [x] 2.2 `scripts/build_bank.py` + tests: emits `data/{generales,senales,auto}.json` + `data/index.json`; out-of-scope excluded, triage flagged.
- [x] 2.3 `scripts/confidence_report.py` + `tests/test_review_queue.py`: low-confidence → review-queue; reviewed ships.
- [ ] 2.4 Author bank + materials.json from PDFs/manual/leyes: schema passes, queue empty, every question has `fundamento` + ≥1 source (size:exception).

## Phase 3: Quiz Engine
- [x] 3.1 `js/quiz-engine.js` + `js/quiz-engine.test.js` (seedable RNG): 40 unique, no `imageRequired`, floors 8/20/6, essentials force-include, cap-yield, deficit realloc, shuffle/remap, threshold.
- [x] 3.2 `tests/test_engine_parity.py`: pytest runs `node` on fixture → invariants.

## Phase 4: Static Site
- [ ] 4.1 `js/config.js` (40 q, 30 pass, floors, gate) + `js/data-loader.js` + `js/app.js` + jsdom: fetch-error (`file://`), lazy fetch.
- [ ] 4.2 quiz/study/materials views + jsdom: answer feedback, empty filter, 5 cards, placeholder+`srcPage` link.
- [ ] 4.3 `index.html` + `css/style.css`: nav, `<script type="module">`, relative `./data/` refs.

## Phase 5: Deploy + Docs
- [ ] 5.1 `.github/workflows/deploy.yml` + `.nojekyll`: Pages from `main@/`, fails if review-queue non-empty.
- [ ] 5.2 `README.md`: usage, authoring, deploy.