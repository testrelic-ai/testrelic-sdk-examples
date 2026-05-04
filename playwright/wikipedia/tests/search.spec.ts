import { test, expect } from '@testrelic/playwright-analytics/fixture';

test.describe('Wikipedia Search', { tag: ['@e2e'] }, () => {
  test('search with Enter key navigates to results', async ({ page }) => {
    await page.goto('https://en.wikipedia.org/wiki/Main_Page');
    const searchInput = page.locator('input[name="search"]').first();
    await searchInput.fill('Playwright testing');
    await searchInput.press('Enter');
    await page.waitForLoadState('domcontentloaded');
    expect(page.url()).toContain('Playwright');
  });

  test('search suggestions appear while typing', async ({ page }) => {
    await page.goto('https://en.wikipedia.org/wiki/Main_Page');
    const searchInput = page.locator('input[name="search"]').first();
    await searchInput.fill('JavaScript');
    await expect(
      page.locator('.cdx-menu-item').first(),
    ).toBeVisible({ timeout: 5_000 });
  });

  test('clicking a suggestion navigates to the article', async ({ page }) => {
    await page.goto('https://en.wikipedia.org/wiki/Main_Page');
    const searchInput = page.locator('input[name="search"]').first();
    await searchInput.fill('Node.js');
    await expect(
      page.locator('.cdx-menu-item').first(),
    ).toBeVisible({ timeout: 5_000 });
    await page.locator('.cdx-menu-item').first().click();
    await page.waitForLoadState('domcontentloaded');
    expect(page.url()).not.toContain('Main_Page');
  });
});
