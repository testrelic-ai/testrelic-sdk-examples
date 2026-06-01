import { test, expect } from '@testrelic/playwright-analytics/fixture';

test.describe('Google Search', { tag: ['@e2e'] }, () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://www.google.com');
    try {
      await page.locator('button:has-text("Accept all")').click({ timeout: 3_000 });
    } catch {
      // No consent dialog
    }
  });

  test('search query navigates to results page', async ({ page }) => {
    const searchInput = page.locator('textarea[name="q"], input[name="q"]').first();
    await searchInput.fill('Playwright testing framework');
    await searchInput.press('Enter');
    await page.waitForLoadState('domcontentloaded');
    expect(page.url()).toContain('q=Playwright');
  });

  test('search results contain links', async ({ page }) => {
    const searchInput = page.locator('textarea[name="q"], input[name="q"]').first();
    await searchInput.fill('Playwright testing framework');
    await searchInput.press('Enter');
    await page.waitForLoadState('domcontentloaded');
    const links = page.locator('#search a');
    await expect(links.first()).toBeVisible({ timeout: 10_000 });
  });

  test('search suggestions appear while typing', async ({ page }) => {
    const searchInput = page.locator('textarea[name="q"], input[name="q"]').first();
    await searchInput.fill('playwright');
    await expect(
      page.locator('[role="listbox"]').first(),
    ).toBeVisible({ timeout: 5_000 });
  });
});
