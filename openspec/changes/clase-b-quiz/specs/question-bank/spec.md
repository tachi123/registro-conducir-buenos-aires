# Question Bank Specification

## Purpose

Single source of truth for the Clase B quiz app: per-section JSON files containing every in-scope question from the official battery (~680 questions), manually authored answer keys (`correct` + `fundamento` + `sources[]` with confidence flags), and image-question placeholders. All app views MUST read question data from these files — no hardcoded questions.

## Requirements

### Requirement: JSON schema and data integrity

Every question object MUST conform to the schema: `id` (unique slug `{section}-{seq}`), `number` (nullable; duplicates allowed), `section`, `category` (`generales` | `senales` | `especificas-auto`), `subcategory`, `question`, `options[]` (`key` + `text`), `correct` (single key), `answerType` (`single` | `truefalse`), `fundamento`, `sources[]` (`material`, `ref`, `page`), `essential` (boolean), `imageRef` (nullable), `imageRequired` (boolean), `srcFile`, `srcPage`, `regionNote` (nullable). The bank MUST use `id` as the join key; `number` gaps (e.g. 34, 193) and duplicate numbers (e.g. 225 image pair) MUST NOT break loading. The bank MUST be packaged as one file per section plus `data/index.json` listing the sections.

#### Scenario: Valid question loads

- GIVEN a question object with all required fields
- WHEN the bank is built and loaded
- THEN it passes schema validation and is addressable by `id`

#### Scenario: Duplicate battery numbers coexist

- GIVEN two questions both numbered 225 (image pair) with distinct `id`s
- WHEN the app joins or renders them
- THEN both are retained and referenced only by `id`

### Requirement: Extraction and build pipeline

A build script MUST extract questions from the official battery text (`cuestionario.pdf` via `pdftotext`) into per-section JSON files. The script MUST clean extraction artifacts (mojibake accents, line-wrapped options, split V/F grids), record `srcFile` + `srcPage` per question, and assign sequential `id`s to unnumbered blocks. Regeneration from the source PDF MUST remain possible.

#### Scenario: Mojibake cleaned

- GIVEN raw extracted text containing artifacts such as `Ã©`
- WHEN the build runs
- THEN the JSON contains the correctly decoded accent character

#### Scenario: Unnumbered block addressed

- GIVEN a question in an unnumbered block (e.g. "Conducción segura")
- WHEN the build assigns ids
- THEN it receives `{section}-{seq}` and a valid `srcPage`

### Requirement: Answer-key authoring and review queue

Because the battery has NO answer key, each question's `correct`, `fundamento`, and `sources[]` MUST be authored manually from manual/law/ANSV evidence. Every authored answer MUST carry a `confidence` flag. Questions below the confidence threshold MUST be listed in a review report/queue and MUST be excluded from release until reviewed.

#### Scenario: Confident answer ships

- GIVEN a question authored with `confidence` at or above threshold and reviewed
- WHEN the build runs
- THEN it is included in the shipped bank

#### Scenario: Low confidence flagged

- GIVEN a question with `confidence` below threshold
- WHEN the build/report runs
- THEN it is listed in the review queue and excluded from release until reviewed

### Requirement: Image-question placeholders

Image-dependent questions (stem meaningless without the visual) MUST carry `imageRef` (nullable placeholder path) and `srcPage` (link to the source PDF page). `imageRequired: true` MUST mark stems that are not answerable from text alone.

#### Scenario: Placeholder with source link

- GIVEN an `imageRequired` question
- WHEN rendered in study mode
- THEN a placeholder and a `srcPage` link to the source PDF page are shown

### Requirement: Clase B scope taxonomy

The bank MUST contain only Clase B in-scope sections (general sections 0–14 plus "Auto y Camioneta"). Out-of-scope sections (moto, tracción a sangre, cargas, urgencia, taxis, transporte de pasajeros, camiones) MUST be excluded. A manual triage pass MUST reclassify questions mislabeled for Clase B (e.g. moto-flavored questions buried in general sections).

#### Scenario: Out-of-scope section excluded

- GIVEN extracted questions from the moto section
- WHEN the build runs
- THEN they are absent from every shipped bank file

#### Scenario: Triage reclassification

- GIVEN a moto-part question numbered inside a general section
- WHEN the triage pass runs
- THEN it is flagged and moved out of Clase B scope