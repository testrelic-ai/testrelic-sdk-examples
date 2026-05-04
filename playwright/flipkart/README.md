# Flipkart Example — @testrelic/playwright-analytics

Playwright tests against Flipkart demonstrating e-commerce navigation tracking, search, product page visits, and category browsing with popup handling.

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
| `homepage.spec.ts` | Homepage load, search bar visibility, navigation header |
| `search.spec.ts` | Product search, results page verification |
| `product-page.spec.ts` | Navigate from search results to a product page |
| `category-browse.spec.ts` | Category page load, product navigation with back button |

## Notes

Flipkart may show a login popup on first visit. Tests include `try/catch` patterns to dismiss it automatically.

## Metadata Features Demonstrated (Schema 1.1.0)

- **`testType: 'e2e'`** — All tests tagged `@e2e` at the describe block level
- **`tags: ['@e2e']`** — Tags inherited by all tests in each describe block
- **`status: 'skipped'`** — Product page tests conditionally skip when elements are unavailable
- **`testId`** — Auto-generated deterministic hash per test
- **`filePath`**, **`suiteName`** — Auto-extracted from test location
