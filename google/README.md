# Google Example — @testrelic/playwright-analytics

Playwright tests against Google demonstrating search interaction, results page navigation, back button tracking, and pagination.

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
| `homepage.spec.ts` | Search page load, Google logo, search button |
| `search.spec.ts` | Search query submission, results verification, autocomplete |
| `results-navigation.spec.ts` | Click result and go back, pagination to page 2 |

## Notes

Google may show a consent dialog in certain regions (EU). Tests include `try/catch` patterns to dismiss it automatically.

## Metadata Features Demonstrated (Schema 1.1.0)

- **`retries: 1`** — Enables flaky detection; tests that fail then pass on retry get `isFlaky: true` and `retryStatus`
- **Mixed tags** — Homepage tests combine `@e2e` (describe-level) with `@smoke` (test-level)
- **`testType: 'e2e'`** — Classified from `@e2e` tag (takes precedence over `@smoke`)
- **`status: 'skipped'`** — Results navigation test conditionally skips in some regions
- **`testId`** — Auto-generated deterministic hash per test
