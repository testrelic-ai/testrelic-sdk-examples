# TestRelic SDK Examples

This repository is organized into **three** areas:

| Area | Stack | What it demonstrates |
|------|--------|----------------------|
| [playwright](./playwright) | Playwright + [`@testrelic/playwright-analytics`](https://www.npmjs.com/package/@testrelic/playwright-analytics) | Web E2E and API tests on real sites, analytics reports |
| [appium](./appium) | WebdriverIO + Appium 2 + [`@testrelic/appium-analytics`](https://www.npmjs.com/package/@testrelic/appium-analytics) | Android UI tests on the **real Wikipedia app** from a shared APK, local + optional cloud reports |
| [maestro](./maestro) | Maestro + [`@testrelic/maestro-analytics`](https://www.npmjs.com/package/@testrelic/maestro-analytics) | Mobile flows on the same Wikipedia app |

Shared mobile binaries live under [mobile-apps](./mobile-apps) (ignored by git). Populate **`wikipedia.apk`** with:

```bash
node mobile-apps/download-wikipedia-apk.mjs
```

See [mobile-apps/README.md](./mobile-apps/README.md).

**Windows:** the [Makefile](./Makefile) targets use bash-style `cd` chains. Use **Git Bash** or **WSL**, or run the `npm` / `npx` commands from each project’s README directly in PowerShell.

---

## Playwright ([`playwright/`](./playwright))

See [playwright/README.md](./playwright/README.md) for the examples table and commands.

```bash
cd playwright/api-testing
npm install
npx playwright test
```

Browser examples need Chromium:

```bash
cd playwright/wikipedia
npm install
npx playwright install chromium
npx playwright test
```

### E2E (browser)

Uses the `page` fixture for navigation tracking — load timing, DOM content loaded, network idle, and request statistics.

```typescript
import { test, expect } from '@testrelic/playwright-analytics/fixture';

test('homepage loads', { tag: ['@e2e'] }, async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page).toHaveTitle(/Example/);
});
```

### API only

Uses the `request` fixture — no browser. See [playwright/api-testing](./playwright/api-testing).

### Unified (browser + API)

Uses both `page` and `request` in one test. See [playwright/unified-testing](./playwright/unified-testing).

### Playwright configuration

Add the TestRelic reporter to `playwright.config.ts` (each example under [`playwright/`](./playwright) already does this, including optional **cloud** upload when `TESTRELIC_API_KEY` is set — with repo-root `dotenv`, [`scripts/apply-testrelic-staging-env.mjs`](./scripts/apply-testrelic-staging-env.mjs) copies **`TESTRELIC_STAGE_API_KEY` → `TESTRELIC_API_KEY`** and sets **`TESTRELIC_CLOUD_ENDPOINT`** to **`TESTRELIC_STAGE_CLOUD_ENDPOINT`** or, if unset, **`https://stage.testrelic.ai/api/v1`**; see [`.env.example`](./.env.example)):

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
      cloud: {
        apiKey: process.env.TESTRELIC_API_KEY,
        upload: 'both',
        uploadArtifacts: true,
        artifactMaxSizeMb: 10,
        timeout: 30_000,
      },
    }],
  ],
});
```

See [playwright/README.md](./playwright/README.md) for cloud setup and per-example `.testrelic/testrelic-config.json` project names.

#### API tracking options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `trackApiCalls` | `boolean` | `true` | Enable/disable API call tracking |
| `captureRequestBody` | `boolean` | `true` | Capture request body |
| `captureResponseBody` | `boolean` | `true` | Capture response body |
| `redactHeaders` | `string[]` | `['authorization', 'cookie', 'set-cookie', 'x-api-key']` | Headers to redact |
| `redactBodyFields` | `string[]` | `['password', 'secret', 'token', 'apiKey', 'api_key']` | Body fields to redact |
| `apiIncludeUrls` | `(string \| RegExp)[]` | `[]` | Only track matching URLs |
| `apiExcludeUrls` | `(string \| RegExp)[]` | `[]` | Exclude matching URLs |

See [playwright/api-testing](./playwright/api-testing) for configuration demos and the [npm package readme](https://www.npmjs.com/package/@testrelic/playwright-analytics) for the full reference.

---

## Appium ([`appium/`](./appium))

Uses **`../mobile-apps/wikipedia.apk`** (see [mobile-apps/README.md](./mobile-apps/README.md)) and **`@testrelic/appium-analytics`** (service + reporter in [`wdio.conf.ts`](./appium/wdio.conf.ts), optional cloud when `TESTRELIC_API_KEY` is set). See [appium/README.md](./appium/README.md).

```bash
cd appium
npm install
npx appium driver install uiautomator2
npm test
```

---

## Maestro ([`maestro/`](./maestro))

Install the Wikipedia APK on a device or emulator, then:

```bash
cd maestro
npm install
npm test
```

Uses the TestRelic Maestro wrapper (`testrelic-maestro`) and [`.testrelic/testrelic-config.json`](./maestro/.testrelic/testrelic-config.json) for dashboard project naming and optional cloud. Details: [maestro/README.md](./maestro/README.md).

---

## Prerequisites

- **Node.js** >= 18
- **Playwright** >= 1.35.0 (Playwright examples)
- **Android SDK / Maestro CLI / JDK** as described in the Appium and Maestro READMEs

## License

MIT
