# Quiz Mode Specification

## Purpose

Simulated 40-question Clase B exam drawn from the question bank: stratified random sampling with category floors, force-included essential questions, no repeats, shuffled options, and mandatory after-answer feedback (correct/incorrect + `fundamento` + `sources[]`). The feedback loop is the core study mechanism — no feedback-skipping.

## Requirements

### Requirement: Exam composition (40 questions)

Every exam MUST contain exactly 40 distinct questions sampled without replacement from `data/*.json`. Every generated exam MUST satisfy: señales ≤ 8, generales ≥ 20, auto ≥ 6. Questions with `imageRequired: true` MUST be excluded from sampling while the image pipeline is absent.

#### Scenario: Floors respected

- GIVEN a full in-scope bank
- WHEN an exam is generated
- THEN it contains 40 unique questions with señales ≤ 8, generales ≥ 20, auto ≥ 6, and no `imageRequired` items

#### Scenario: Category too small for its floor

- GIVEN a category with fewer candidates than its floor
- WHEN an exam is generated
- THEN the category contributes all of its candidates and the residual is filled from other categories without repeats

### Requirement: Essential force-include

Questions flagged `essential: true` MUST be force-included in every exam — the full subset when slots allow, otherwise a deterministic prioritized subset. Essential inclusion MUST take precedence over category caps; when essential items exceed a cap, the cap yields for those items and the remaining draw is reallocated.

#### Scenario: Essential always present

- GIVEN a bank with ~50 essential questions
- WHEN any exam is generated
- THEN every essential question of the chosen subset appears in that exam

#### Scenario: Essential exceeds señales cap

- GIVEN more essential señales questions than the 8-question cap
- WHEN an exam is generated
- THEN those essential items are included and the remaining señales draw is reduced accordingly

### Requirement: Mandatory after-answer feedback

After EVERY answer the app MUST immediately show: correct/incorrect, the `fundamento`, and `sources[]` chips (material + ref/page) — regardless of correctness. There MUST be no skip-feedback mode. Options MUST be presented in shuffled order with the `correct` key remapped per render.

#### Scenario: Feedback after every answer

- GIVEN a question answered correctly or incorrectly
- WHEN the answer is submitted
- THEN feedback shows the result, fundamento, and source chips before any next-question action

#### Scenario: Shuffled option keys

- GIVEN options displayed in shuffled order
- WHEN the user picks the displayed correct option
- THEN the engine marks it correct using the remapped display key, not the stored `correct` value

### Requirement: Scoring and pass threshold

Each question MUST award 1 point. The pass threshold MUST be configurable through a single configuration point, with default 30/40 (75%). The app MUST show progress during the exam and, at the end, the final score with pass/fail against the threshold.

#### Scenario: Default threshold applied

- GIVEN the default threshold of 30/40
- WHEN the exam ends with 30/40
- THEN the result is PASS (with 29/40 it is FAIL)

#### Scenario: Threshold overridden

- GIVEN a configured threshold of 28/40
- WHEN the exam ends with 28/40
- THEN the result is PASS per the configured value