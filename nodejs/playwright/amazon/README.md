# Amazon example — multi-page crawl

One Playwright spec visits **several Amazon.com URLs in a single test** (home, bestsellers, deals hub, site map, deals query, help). Each `page.goto` (and the optional deals link click) is recorded on the **TestRelic navigation timeline** when using [`@testrelic/playwright-analytics/fixture`](https://www.npmjs.com/package/@testrelic/playwright-analytics).

Amazon may throttle or alter pages for automation; this example uses **relaxed URL assertions** (`amazon.com` only). If a run is flaky, increase timeouts in [`playwright.config.ts`](playwright.config.ts) or run headed locally.

## Run

```bash
cd playwright/amazon
npm install
npx playwright install chromium
npm test
```

Cloud upload follows the same [Playwright cloud / `.env`](../README.md) setup as the other examples (`playwright-amazon` in [`.testrelic/testrelic-config.json`](.testrelic/testrelic-config.json)).
