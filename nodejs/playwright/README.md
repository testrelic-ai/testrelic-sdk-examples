# Playwright examples — `@testrelic/playwright-analytics`

Standalone projects using [`@testrelic/playwright-analytics`](https://www.npmjs.com/package/@testrelic/playwright-analytics) for navigation timelines, API tracking, network stats, and HTML reports.

## Examples

| Example | Type | Targets | What it demonstrates |
|---------|------|---------|------------------------|
| [api-testing](./api-testing) | API only | JSONPlaceholder API | CRUD, chaining, assertions, config options, error handling |
| [unified-testing](./unified-testing) | E2E + API | Wikipedia + JSONPlaceholder | Browser + API in the same test |
| [wikipedia](./wikipedia) | E2E | en.wikipedia.org | Homepage, search, navigation, media-heavy pages |
| [flipkart](./flipkart) | E2E | flipkart.com | Homepage, search, product pages, categories |
| [google](./google) | E2E | google.com | Homepage, search, results navigation |
| [amazon](./amazon) | E2E | amazon.com | Single-test multi-page crawl (timeline navigations) |

## Quick start

```bash
cd playwright/api-testing   # or any other example under this folder
npm install
npx playwright test
```

For browser-based examples:

```bash
cd playwright/wikipedia     # or flipkart, google, amazon, unified-testing
npm install
npx playwright install chromium
npx playwright test
```

## TestRelic Cloud (optional)

Each example uses **`@testrelic/playwright-analytics` ^2.7.0** with a `cloud` block in `playwright.config.ts` (`apiKey: process.env.TESTRELIC_API_KEY`, `upload: 'both'`, artifact limits). Local JSON/HTML reports still run when no key is set.

**Staging vs production:** `@testrelic/core` applies **`process.env.TESTRELIC_API_KEY`** and **`process.env.TESTRELIC_CLOUD_ENDPOINT` last** when merging cloud config, so they override `playwright.config.ts` and `.testrelic/testrelic-config.json`. If both **`TESTRELIC_STAGE_API_KEY`** and **`TESTRELIC_API_KEY`** are in `.env`, production would always win for the key. Each `playwright.config.ts` calls [`scripts/apply-testrelic-staging-env.mjs`](../scripts/apply-testrelic-staging-env.mjs) after `dotenv.config()` so that:

1. A non-empty **`TESTRELIC_STAGE_API_KEY`** is copied onto **`TESTRELIC_API_KEY`**.
2. **`TESTRELIC_CLOUD_ENDPOINT`** is set to **`TESTRELIC_STAGE_CLOUD_ENDPOINT`** when that variable is non-empty; otherwise it defaults to **`https://stage.testrelic.ai/api/v1`** (staging API — production remains **`https://platform.testrelic.ai/api/v1`** in committed `.testrelic` when you are not using a stage key). See [`.env.example`](../.env.example).

`playwright.config.ts` loads **`../../.env`** from the repository root (via `dotenv`) before that step. New VS Code / Cursor integrated terminals also load that file via [`.vscode/settings.json`](../.vscode/settings.json).

1. Create or copy an API key from the TestRelic dashboard (**Settings → API Keys**).
2. Set **`TESTRELIC_API_KEY`** for production, or for staging set **`TESTRELIC_STAGE_API_KEY`** (shell, CI, or repo-root `.env`). Optionally set **`TESTRELIC_STAGE_CLOUD_ENDPOINT`** to override the default staging API **`https://stage.testrelic.ai/api/v1`**.
3. Each project has a committed [`.testrelic/testrelic-config.json`](./api-testing/.testrelic/testrelic-config.json) template with `"apiKey": "$TESTRELIC_API_KEY"` and a distinct `testrelic-repo.name` per example so runs show up separately in the cloud UI.

Optional tuning: adjust `cloud.upload`, `cloud.uploadArtifacts`, `cloud.artifactMaxSizeMb`, or `cloud.timeout` in `playwright.config.ts` (see the [package README](https://www.npmjs.com/package/@testrelic/playwright-analytics)). Advanced: `npx testrelic merge …` and `npx testrelic serve …` are documented on npm for sharded runs and large local reports.

See the [repository root README](../README.md) for broader reporter option tables.
