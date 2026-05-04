# Unified Testing Example — @testrelic/playwright-analytics

Demonstrates using **both browser-based E2E tests and API tests** in a single project with TestRelic analytics. The unified `testRelicFixture` provides both `page` (browser navigation tracking) and `request` (API call tracking) fixtures.

## Setup

```bash
# From monorepo root
pnpm install
pnpm build

# Install browsers (needed for E2E tests)
cd examples/unified-testing
npx playwright install chromium
```

## Run

```bash
npx playwright test
```

## Tests

| Spec File | Tags | Fixtures Used | What It Demonstrates |
|-----------|------|---------------|---------------------|
| `e2e-navigation.spec.ts` | `@e2e` | `page` | Browser navigation, page load timing, network stats |
| `api-operations.spec.ts` | `@api` | `request` | HTTP methods (GET, POST, PUT, DELETE), API chaining |
| `unified-workflow.spec.ts` | `@e2e`, `@api` | `page` + `request` | Combined browser + API tests in a single test |

## Key Difference from API-Only Example

- **API-only** (`examples/api-testing`): Uses `testRelicApiFixture` — provides only `request`, no browser dependency
- **Unified** (this example): Uses `testRelicFixture` — provides both `page` and `request`

```typescript
// Unified: import directly from the fixture module
import { test, expect } from '@testrelic/playwright-analytics/fixture';

// Both page and request are available in the same test
test('unified test', async ({ page, request }) => {
  const apiData = await request.get('https://api.example.com/data');
  await page.goto('https://example.com');
});
```

## TestRelic Report Features

- **Navigation timeline**: Page load timing, DOM content loaded, network idle
- **API call tracking**: Method, URL, status, request/response bodies, response time
- **Unified view**: Both navigation and API calls visible in the same test's drawer
- **Screenshots and video**: Captured for browser-based tests
- **Network stats**: Request counts, transferred bytes per navigation
