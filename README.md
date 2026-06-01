# TestRelic SDK Examples

A single monorepo of TestRelic SDK demos, organized by **language** and then **framework**:

```
nodejs/     JavaScript / TypeScript demos (@testrelic/* npm packages)
  playwright/    Web E2E + API tests
  appium/        Android UI tests (WebdriverIO + Appium 2)
  maestro/       Mobile flows
  mobile-apps/   Shared mobile binaries (apk/ipa ignored by git)
python/     Python demos (testrelic-* PyPI packages)
  testrelic-pytest-demo/   pytest across all API protocols (REST/GraphQL/gRPC/
                           WebSocket/Kafka/MCP) + Playwright + DeepEval + Appium,
                           uploading real runs to the TestRelic cloud
```

## NodeJS demos ([`nodejs/`](./nodejs))

| Area | Stack | What it demonstrates |
|------|--------|----------------------|
| [playwright](./nodejs/playwright) | Playwright + [`@testrelic/playwright-analytics`](https://www.npmjs.com/package/@testrelic/playwright-analytics) | Web E2E and API tests (incl. multi-page Amazon crawl), analytics reports |
| [appium](./nodejs/appium) | WebdriverIO + Appium 2 + [`@testrelic/appium-analytics`](https://www.npmjs.com/package/@testrelic/appium-analytics) | Android UI tests on the **real Wikipedia app** from a shared APK, local + optional cloud reports |
| [maestro](./nodejs/maestro) | Maestro + [`@testrelic/maestro-analytics`](https://www.npmjs.com/package/@testrelic/maestro-analytics) | Mobile flows on the same Wikipedia app |

## Python demos ([`python/`](./python))

| Area | Stack | What it demonstrates |
|------|--------|----------------------|
| [testrelic-pytest-demo](./python/testrelic-pytest-demo) | pytest + `testrelic-pytest` / `testrelic-playwright` / `testrelic-deepeval` / `testrelic-appium` | All API protocols (REST/GraphQL/gRPC/WebSocket/Kafka/MCP), an LLM-eval suite, and a regression→recovery seed arc, all uploading to the TestRelic cloud. See [python/testrelic-pytest-demo/README.md](./python/testrelic-pytest-demo/README.md). |

> **Note:** the Python demo currently installs the SDKs editable from the
> private `testrelic-platform` monorepo (a sibling checkout) because the protocol
> features require `testrelic-pytest >= 0.2` while PyPI is at `0.1.1`. Once `>= 0.3`
> is published, its `requirements.txt` switches to pinned PyPI versions.

Shared mobile binaries live under [nodejs/mobile-apps](./nodejs/mobile-apps) (ignored by git). Populate **`wikipedia.apk`** with:

```bash
node nodejs/mobile-apps/download-wikipedia-apk.mjs
```

See [nodejs/mobile-apps/README.md](./nodejs/mobile-apps/README.md).

**Windows:** the [Makefile](./Makefile) targets use bash-style `cd` chains. Use **Git Bash** or **WSL**, or run the `npm` / `npx` commands from each project’s README directly in PowerShell.

---

## Playwright ([`nodejs/playwright/`](./nodejs/playwright))

See [nodejs/playwright/README.md](./nodejs/playwright/README.md) for the examples table and commands.

```bash
cd nodejs/playwright/api-testing
npm install
npx playwright test
```

Browser examples need Chromium:

```bash
cd nodejs/playwright/wikipedia
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

See [nodejs/playwright/README.md](./nodejs/playwright/README.md) for cloud setup and per-example `.testrelic/testrelic-config.json` project names.

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

See [nodejs/playwright/api-testing](./nodejs/playwright/api-testing) for configuration demos and the [npm package readme](https://www.npmjs.com/package/@testrelic/playwright-analytics) for the full reference.

---

## Appium ([`nodejs/appium/`](./nodejs/appium))

Uses **`../mobile-apps/wikipedia.apk`** (see [nodejs/mobile-apps/README.md](./nodejs/mobile-apps/README.md)) and **`@testrelic/appium-analytics`** (service + reporter in [`wdio.conf.ts`](./nodejs/appium/wdio.conf.ts), optional cloud when `TESTRELIC_API_KEY` is set). See [nodejs/appium/README.md](./nodejs/appium/README.md).

```bash
cd nodejs/appium
npm install
npx appium driver install uiautomator2
npm test
```

---

## Maestro ([`nodejs/maestro/`](./nodejs/maestro))

Install the Wikipedia APK on a device or emulator, then:

```bash
cd nodejs/maestro
npm install
npm test
```

Uses the TestRelic Maestro wrapper (`testrelic-maestro`) and [`.testrelic/testrelic-config.json`](./nodejs/maestro/.testrelic/testrelic-config.json) for dashboard project naming and optional cloud. Details: [nodejs/maestro/README.md](./nodejs/maestro/README.md).

---

## Python ([`python/testrelic-pytest-demo/`](./python/testrelic-pytest-demo))

```bash
cd python/testrelic-pytest-demo
python -m venv .venv && .venv/Scripts/activate   # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python verification/verify.py    # offline proof — asserts every metric reaches the wire
```

Covers `testrelic-pytest` across all API protocols, plus `testrelic-deepeval`,
`testrelic-playwright`, and `testrelic-appium`. See
[python/testrelic-pytest-demo/README.md](./python/testrelic-pytest-demo/README.md).

---

## Prerequisites

- **Node.js** >= 18 (NodeJS demos)
- **Playwright** >= 1.35.0 (Playwright examples)
- **Python** >= 3.10 (Python demos)
- **Android SDK / Maestro CLI / JDK** as described in the Appium and Maestro READMEs

## License

MIT
