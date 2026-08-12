# Study Summaries Specification

## Purpose

Hand-authored key-idea cheat-sheet summaries per study material, tagged with license classes and browsed through a data-driven license filter with an empty state — the study companion to the five `material-summaries` orientation cards.

## Requirements

### Requirement: Summary data file (`data/resumenes.json`)

`data/resumenes.json` MUST be hand-authored (never generated), an array with exactly one entry per study material: `cuestionario`, `manual`, `ansv-senales`, `ley-24449`, `ley-13927` (5 entries). Each entry MUST provide `id`, `title`, `ideasClave` (non-empty array of short key-idea bullets — cheat-sheet density, not a full digest), and `licencias` (non-empty array of license tags). The schema MUST allow multiple tags per entry; initial data uses `["auto"]`. Bullets SHOULD cite their source material with a reference (page/chapter/article) inline where feasible, keeping content reviewable per the project's hand-authored, confidence-review discipline.

#### Scenario: All five materials present

- GIVEN the file is loaded
- WHEN its entries are enumerated
- THEN there are exactly 5, with ids `cuestionario`, `manual`, `ansv-senales`, `ley-24449`, `ley-13927`

#### Scenario: Entry schema shape

- GIVEN any entry
- WHEN it is validated
- THEN `id` and `title` are non-empty strings, `ideasClave` and `licencias` are non-empty string arrays, and an entry with two license tags validates (multi-tag allowed)

#### Scenario: Bullets concise and referenced

- GIVEN an authored entry
- WHEN its bullets are inspected
- THEN each bullet states one key idea and cites material + ref (page/chapter/article) where feasible

### Requirement: Data-driven license filter

The resumenes view MUST render a license filter `<select>` whose options derive at render time from the union of `licencias` values across all entries — never hardcoded. Selecting a tag MUST narrow the cards to entries whose `licencias` include it; the default "Todas" option MUST show all entries.

#### Scenario: Options come from the data

- GIVEN entries all tagged `["auto"]`
- WHEN the view renders
- THEN the filter offers "Todas" plus exactly one option: "auto"

#### Scenario: New tag appears without code changes

- GIVEN data later gains an entry with `licencias: ["moto"]`
- WHEN the view renders
- THEN a "moto" option appears with no code edits

#### Scenario: Filter narrows the cards

- GIVEN a mix of tagged entries
- WHEN "auto" is selected
- THEN only auto-tagged entries are shown

### Requirement: Resumenes view and navigation

A new `resumenesView` in `js/views.js` MUST follow the `{ load(), render(content, data) }` registry pattern and load via `dataUrl('resumenes.json')`. It MUST render one card per entry: title, license chips, and `ideasClave` as a bullet list. `js/app.js` MUST add a `resumenes` entry to `VIEW_NAMES` so the nav shows a "Resúmenes" link and the `#resumenes` route renders the view.

#### Scenario: Cards render per material

- GIVEN `#resumenes` opens
- WHEN the view renders
- THEN each entry shows as a card with title, license chips, and an `ideasClave` bullet list

#### Scenario: Nav entry and route

- GIVEN the app boots
- WHEN the nav is built
- THEN a "Resúmenes" link to `#resumenes` exists and activates the view on click

### Requirement: Empty state for unmatched filters

A license filter selection matching no summaries MUST show an empty-state message instead of a blank area (study-mode precedent).

#### Scenario: No matches

- GIVEN a filter selection with no matching entries
- WHEN it is applied
- THEN an empty-state message is shown in place of the card list

### Requirement: Automated test coverage

Vitest tests in `js/` MUST cover the `resumenes.json` data shape (5 entries, required fields, multi-tag allowed), filter options deriving from the data (including a new tag appearing without code changes), filter narrowing, and the empty state.

#### Scenario: Suite exercises view and data

- GIVEN the vitest suite runs
- WHEN data-shape, derived-options, filtering, and empty-state cases are asserted (new describe block in `js/views.test.js` or a sibling test file)
- THEN they pass alongside the existing suite