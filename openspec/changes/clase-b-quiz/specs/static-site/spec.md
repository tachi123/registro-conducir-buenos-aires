# Static Site Specification

## Purpose

A fully static HTML/CSS/JS application (no backend) that serves quiz mode, study mode, and material summaries from the JSON question bank, deployable to GitHub Pages.

## Requirements

### Requirement: Static architecture and data loading

The app MUST be fully static: HTML/CSS/JS + JSON only, with no server and no server-side rendering. It MUST fetch the bank via `data/index.json` and the per-section JSON files; section files MAY be lazy-loaded on demand. A fetch failure MUST surface a clear error state rather than a silent blank screen.

#### Scenario: Lazy section loading

- GIVEN the app served over HTTP(S)
- WHEN the user opens a section view
- THEN the corresponding section JSON is fetched and rendered

#### Scenario: Fetch failure handled

- GIVEN an unreachable or missing JSON file (e.g. the app opened via `file://`)
- WHEN the app attempts to load it
- THEN a friendly error message is shown and the app remains usable for other views

### Requirement: GitHub Pages deployment

The app MUST be deployable to GitHub Pages from repository content alone (e.g. gh-pages branch or Actions workflow). All asset and data references MUST be relative-safe so the site also works under a subpath such as `/{org}/{repo}/`.

#### Scenario: Deployed site loads

- GIVEN the static artifacts published to GitHub Pages
- WHEN the Pages URL is opened
- THEN quiz, study, summaries, and question data all load correctly

#### Scenario: Subpath-safe references

- GIVEN deployment under `/{org}/{repo}/`
- WHEN the app loads
- THEN relative references resolve without path-prefix errors