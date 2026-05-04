import { test, expect } from '@testrelic/playwright-analytics/fixture';

test.describe('Wikipedia Media-Heavy Pages', { tag: ['@e2e'] }, () => {
  test('featured pictures page loads many images', async ({ page }) => {
    await page.goto('https://en.wikipedia.org/wiki/Wikipedia:Featured_pictures');
    await page.waitForLoadState('domcontentloaded');
    const images = await page.locator('img').count();
    expect(images).toBeGreaterThan(5);
  });

  test('featured pictures page has exact image inventory', async ({ page }) => {
    // Marked as expected-to-fail: the exact image count varies as Wikipedia
    // editors rotate featured content. Demonstrates expectedStatus metadata —
    // the report will show expectedStatus: 'failed', actualStatus: 'failed'.
    test.fail();
    await page.goto('https://en.wikipedia.org/wiki/Wikipedia:Featured_pictures');
    await page.waitForLoadState('domcontentloaded');
    const images = await page.locator('img').count();
    expect(images).toBe(9999);
  });
});
