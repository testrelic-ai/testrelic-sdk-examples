import { test, expect } from '@testrelic/playwright-analytics/fixture';

test.describe('Wikipedia Homepage', () => {
  test('loads the main page', { tag: ['@e2e'] }, async ({ page }) => {
    await page.goto('https://en.wikipedia.org/wiki/Main_Page');
    await expect(page.locator('#mp-welcome')).toBeVisible({ timeout: 10_000 });
    const title = await page.title();
    expect(title).toContain('Wikipedia');
  });

  test('displays featured article section', { tag: ['@e2e'] }, async ({ page }) => {
    await page.goto('https://en.wikipedia.org/wiki/Main_Page');
    await expect(page.locator('#mp-tfa')).toBeVisible({ timeout: 10_000 });
  });

  test('has language selector', { tag: ['@e2e'] }, async ({ page }) => {
    await page.goto('https://en.wikipedia.org/wiki/Main_Page');
    await expect(page.locator('#p-lang-btn')).toBeVisible({ timeout: 10_000 });
  });
});
