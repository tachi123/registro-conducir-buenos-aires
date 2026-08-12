# Study Mode Specification

## Purpose

Category-based browsing of the full question bank with answer + `fundamento` + `sources[]` revealed after answering — the self-paced study loop. Includes placeholder handling for image questions so visuals can still be studied via the source PDF link.

## Requirements

### Requirement: Category browsing and filtering

Study mode MUST render questions from `data/*.json` (no hardcoded questions) and MUST support filtering by `category` (`generales` | `senales` | `especificas-auto`) and `subcategory`. Browsing MUST include all bank questions, including `imageRequired` ones.

#### Scenario: Filter by category

- GIVEN a user in study mode
- WHEN filtering to "senales"
- THEN only senales questions are listed

#### Scenario: Empty filter result

- GIVEN a filter combination with no matching questions
- WHEN it is applied
- THEN an empty-state message is shown instead of a blank screen

### Requirement: Answer reveal with evidence

After the user answers a study question, the app MUST show whether the answer is correct or incorrect plus the `fundamento` and `sources[]` chips (material + ref/page).

#### Scenario: Evidence shown after answering

- GIVEN a study question
- WHEN the user submits an answer
- THEN the result, fundamento, and sources are displayed

### Requirement: Image placeholder links

An `imageRequired` question MUST render an image placeholder plus a `srcPage` link to the source PDF page so the visual can be studied from the original material. Questions with `imageRef: null` MUST render text-only.

#### Scenario: Placeholder with source link

- GIVEN an `imageRequired` question
- WHEN it is rendered
- THEN a placeholder and a `srcPage` link are shown

#### Scenario: Text-only question

- GIVEN a question with `imageRef` null
- WHEN it is rendered
- THEN no placeholder block appears