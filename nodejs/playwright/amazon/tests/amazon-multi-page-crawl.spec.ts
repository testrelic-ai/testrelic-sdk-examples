import type { Page } from '@playwright/test';
import { test, expect } from '@testrelic/playwright-analytics/fixture';

async function dismissCookieBannerIfPresent(page: Page) {
  const accept = page.locator('#sp-cc-accept').first();
  try {
    await accept.click({ timeout: 5_000 });
  } catch {
    // Banner absent or different locale — continue
  }
}

test.describe('Amazon — multi-page crawl (single test)', { tag: ['@e2e'] }, () => {
  test('one test visits several Amazon pages so each navigation is on the TestRelic timeline', async ({
    page,
  }) => {
    const urls = [
      'https://www.amazon.com/',
      'https://www.amazon.com/gp/bestsellers/',
      'https://www.amazon.com/gp/goldbox/',
      'https://www.amazon.com/gp/site-directory/',
      'https://www.amazon.com/gp/deals/?ref_=nav_cs_gb',
      'https://www.amazon.com/gp/help/customer/display.html?nodeId=508510',
    ];

    for (let i = 0; i < urls.length; i++) {
      await page.goto(urls[i], { waitUntil: 'domcontentloaded', timeout: 60_000 });
      if (i === 0) {
        await dismissCookieBannerIfPresent(page);
      }
      await expect(page).toHaveURL(/amazon\.com/i);
    }

    // Same test: in-page link navigation (adds a link-driven load on the timeline).
    const dealsLink = page.getByRole('link', { name: /Today's Deals|Deals|Gold Box/i }).first();
    if (await dealsLink.isVisible({ timeout: 8_000 }).catch(() => false)) {
      await dealsLink.click();
      await page.waitForLoadState('domcontentloaded');
      await expect(page).toHaveURL(/amazon\.com/i);
    }
  });
});
