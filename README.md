# TestRelic SDK Examples

Example projects demonstrating how to use [`@testrelic/playwright-analytics`](https://www.npmjs.com/package/@testrelic/playwright-analytics) for test analytics — capturing navigation timelines, API call tracking, network statistics, failure diagnostics, and interactive HTML reports.

## Examples

| Example | Type | Targets | What It Demonstrates |
|---|---|---|---|
| [api-testing](./api-testing) | API only | JSONPlaceholder API | CRUD operations, API chaining, response assertions, config options, error handling |
| [unified-testing](./unified-testing) | E2E + API | Wikipedia + JSONPlaceholder | Browser navigation and API calls in the same test |
| [wikipedia](./wikipedia) | E2E | en.wikipedia.org | Homepage, search, link navigation, media-heavy pages |
| [flipkart](./flipkart) | E2E | flipkart.com | Homepage, product search, product pages, category browsing |
| [google](./google) | E2E | google.com | Homepage, search queries, results navigation |

## Quick Start

Each example is a standalone Playwright project. Pick any example and run:

```bash
cd api-testing        # or any other example
npm install
npx playwright test
```

For browser-based examples (E2E), you also need to install Chromium:

```bash
cd wikipedia          # or flipkart, google, unified-testing
npm install
npx playwright install chromium
npx playwright test
```

## Testing Modes

### E2E Testing (Browser)

Uses the `page` fixture for browser navigation tracking — page load timing, DOM content loaded, network idle detection, and network request statistics.

```typescript
import { test, expect } from '@testrelic/playwright-analytics/fixture';

test('homepage loads', { tag: ['@e2e'] }, async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page).toHaveTitle(/Example/);
});
```

### API Testing

Uses the `request` fixture for API call tracking — HTTP method, URL, status code, headers, bodies, response times, and assertions. No browser needed.

```typescript
import { test as base } from '@playwright/test';
import { testRelicApiFixture } from '@testrelic/playwright-analytics/api-fixture';
import { expect } from '@testrelic/playwright-analytics/fixture';

const test = base.extend(testRelicApiFixture);

test('fetch posts', { tag: ['@api'] }, async ({ request }) => {
  const response = await request.get('https://jsonplaceholder.typicode.com/posts');
  expect(response.status()).toBe(200);
});
```

### Unified Testing (Browser + API)

Uses **both** `page` and `request` in the same test — the report shows navigation timeline AND API call details together.

```typescript
import { test, expect } from '@testrelic/playwright-analytics/fixture';

test('API data matches UI', { tag: ['@e2e', '@api'] }, async ({ page, request }) => {
  const apiResponse = await request.get('https://api.example.com/user/1');
  const user = await apiResponse.json();

  await page.goto('https://example.com/profile');
  await expect(page.locator('.user-name')).toHaveText(user.name);
});
```

## Configuration

Add the TestRelic reporter to your `playwright.config.ts`:

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: [
    ['list'],
    ['@testrelic/playwright-analytics', {
      outputPath: './test-results/analytics-timeline.json',
      includeStackTrace: true,
      includeCodeSnippets: true,
      includeNetworkStats: true,
    }],
  ],
});
```

### API Tracking Options

| Option | Type | Default | Description |
|---|---|---|---|
| `trackApiCalls` | `boolean` | `true` | Enable/disable API call tracking |
| `captureRequestBody` | `boolean` | `true` | Capture request body for each API call |
| `captureResponseBody` | `boolean` | `true` | Capture response body for each API call |
| `redactHeaders` | `string[]` | `['authorization', 'cookie', 'set-cookie', 'x-api-key']` | Header names to redact |
| `redactBodyFields` | `string[]` | `['password', 'secret', 'token', 'apiKey', 'api_key']` | Body fields to redact |
| `apiIncludeUrls` | `(string \| RegExp)[]` | `[]` | Only track matching URLs |
| `apiExcludeUrls` | `(string \| RegExp)[]` | `[]` | Exclude matching URLs |

See the [api-testing](./api-testing) example for configuration demos and the [full configuration reference](https://www.npmjs.com/package/@testrelic/playwright-analytics) on npm.

## Prerequisites

- **Node.js** >= 18
- **Playwright** >= 1.35.0

## License

MIT
