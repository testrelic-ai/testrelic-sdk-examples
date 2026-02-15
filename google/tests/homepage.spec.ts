import { test, expect } from '@testrelic/playwright-analytics/fixture';

test.describe('Google Homepage', { tag: ['@e2e'] }, () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://www.google.com');
    // Handle consent dialog if it appears (common in EU regions)
    try {
      await page.locator('button:has-text("Accept all")').click({ timeout: 3_000 });
    } catch {
      // No consent dialog
    }
  });

  test('loads the search page', { tag: ['@smoke'] }, async ({ page }) => {
    await expect(
      page.locator('textarea[name="q"], input[name="q"]').first(),
    ).toBeVisible({ timeout: 10_000 });
  });

  test('displays the Google logo', async ({ page }) => {
    await expect(
      page.locator('img[alt="Google"]').first(),
    ).toBeVisible({ timeout: 10_000 });
  });

  test('has the search button', async ({ page }) => {
    await expect(
      page.locator('input[name="btnK"]').first(),
    ).toBeVisible({ timeout: 10_000 });
  });
});
