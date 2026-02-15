# Wikipedia Example — @testrelic/playwright-analytics

Playwright tests against Wikipedia demonstrating navigation tracking, search interaction, back/forward history, and image-heavy page analysis.

## Setup

```bash
npm install
npx playwright install chromium
```

## Run

```bash
npx playwright test
```

The analytics report will be written to `./test-results/analytics-timeline.json`.

## Tests

| File | What it covers |
|---|---|
| `homepage.spec.ts` | Main page load, featured article section, language selector |
| `search.spec.ts` | Search with Enter, autocomplete suggestions, suggestion click |
| `navigation.spec.ts` | Article link clicks, back/forward browser history |
| `media-heavy.spec.ts` | Image-heavy page with network stats tracking, `test.fail()` expected-failure demo |

## Metadata Features Demonstrated (Schema 1.1.0)

- **`testType: 'e2e'`** — Tests tagged `@e2e` (per-test in homepage, per-describe in others)
- **`test.fail()` / `expectedStatus`** — media-heavy spec includes a known expected failure
- **`testId`** — Auto-generated deterministic hash per test
- **`filePath`**, **`suiteName`** — Auto-extracted from test location
