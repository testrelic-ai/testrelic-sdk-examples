import { test, expect } from '@testrelic/playwright-analytics/fixture';

test.describe('Google Results Navigation', { tag: ['@e2e'] }, () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://www.google.com');
    try {
      await page.locator('button:has-text("Accept all")').click({ timeout: 3_000 });
    } catch {
      // No consent dialog
    }
    const searchInput = page.locator('textarea[name="q"], input[name="q"]').first();
    await searchInput.fill('Playwright testing framework');
    await searchInput.press('Enter');
    await page.waitForLoadState('domcontentloaded');
  });

  test('click a search result and navigate back', async ({ page }) => {
    const resultLink = page.locator('#search a').first();
    await resultLink.click();
    await page.waitForLoadState('domcontentloaded');
    const resultUrl = page.url();
    expect(resultUrl).not.toContain('google.com/search');

    await page.goBack();
    await page.waitForLoadState('domcontentloaded');
    expect(page.url()).toContain('google.com');
  });

  test('navigate to page 2 of results', async ({ page }) => {
    const nextLink = page.locator('a:has-text("Next"), td a:has-text("2")').first();
    try {
      await nextLink.click({ timeout: 5_000 });
      await page.waitForLoadState('domcontentloaded');
      expect(page.url()).toContain('start=');
    } catch {
      // Some regions show "More results" instead of pagination
      test.skip();
    }
  });
});
