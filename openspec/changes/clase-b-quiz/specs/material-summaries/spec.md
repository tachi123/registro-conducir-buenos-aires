# Material Summaries Specification

## Purpose

Five "mini-resumen" cards, one per study material, giving the learner orientation before studying: what each material is, what to study in it, and how much it weighs in the exam.

## Requirements

### Requirement: The five material cards

The app MUST render exactly 5 summary cards, one per material: (1) Cuestionario oficial, (2) Manual del Conductor (PBA/ANSV), (3) Libro de Señales de Tránsito (ANSV), (4) Ley Nacional de Tránsito 24.449, (5) Ley Provincial 13.927. Each card MUST show four fields: title, "qué es", "qué estudiar", and "peso en examen" (relative weight). Card content MUST come from data, not from hardcoded markup.

#### Scenario: All cards render

- GIVEN a loaded app
- WHEN the material summaries view opens
- THEN all 5 cards render, each with its four fields

#### Scenario: Weight hierarchy expressed

- GIVEN the Cuestionario oficial card
- WHEN its "peso en examen" is compared with the others
- THEN it ranks highest among the five

### Requirement: Content integrity with study scope

Each card's "qué estudiar" field MUST reflect the material's real scope as used by the question bank (e.g. manual chapters, ANSV sign catalog, law articles).

#### Scenario: Manual card grounded in chapters

- GIVEN the Manual del Conductor card
- WHEN inspected
- THEN its "qué estudiar" guidance references that manual's actual chapters/sections