/**
 * E2E Navigation Tests — Browser-based tests using the `page` fixture.
 *
 * These tests demonstrate TestRelic's browser navigation tracking:
 * page load timing, DOM content loaded, network idle detection, and
 * network request statistics — all captured in the TestRelic report.
 */
import { test, expect } from '@testrelic/playwright-analytics/fixture';

test.describe('E2E Navigation', { tag: ['@e2e'] }, () => {
  test('navigate to Wikipedia homepage and verify title', async ({ page }) => {
    await page.goto('https://en.wikipedia.org/wiki/Main_Page');
    await expect(page).toHaveTitle(/Wikipedia/);
  });

  test('search Wikipedia and navigate to results', async ({ page }) => {
    await page.goto('https://en.wikipedia.org/wiki/Main_Page');

    const searchInput = page.locator('#searchInput').first();
    await searchInput.fill('Playwright');
    await searchInput.press('Enter');

    await page.waitForLoadState('domcontentloaded');
    expect(page.url()).toContain('Playwright');
  });

  test('navigate between Wikipedia pages', async ({ page }) => {
    // Step 1: Start at the main page
    await page.goto('https://en.wikipedia.org/wiki/Main_Page');
    await expect(page).toHaveTitle(/Wikipedia/);

    // Step 2: Navigate to a specific article
    await page.goto('https://en.wikipedia.org/wiki/Software_testing');
    await expect(page).toHaveTitle(/Software testing/);

    // Step 3: Click an internal link to navigate further
    const link = page.locator('a[href="/wiki/Test_automation"]').first();
    if (await link.isVisible()) {
      await link.click();
      await page.waitForLoadState('domcontentloaded');
    }
  });
});
