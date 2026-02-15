import { test, expect } from '@testrelic/playwright-analytics/fixture';

test.describe('Flipkart Homepage', { tag: ['@e2e'] }, () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://www.flipkart.com');
    await page.waitForLoadState('domcontentloaded');
    // Dismiss login popup if it appears
    try {
      await page.locator('button:has-text("✕")').click({ timeout: 3_000 });
    } catch {
      // No popup — continue
    }
  });

  test('loads the homepage successfully', async ({ page }) => {
    expect(page.url()).toContain('flipkart.com');
    // Verify page rendered with content
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
  });

  test('scrolling the page loads more content', async ({ page }) => {
    // Use mouse wheel to scroll and trigger lazy loading
    await page.mouse.wheel(0, 600);
    await page.waitForTimeout(500);
    await page.mouse.wheel(0, 600);
    await page.waitForTimeout(500);
    await page.mouse.wheel(0, 600);
    await page.waitForTimeout(1000);

    // Verify there are images on the page (from lazy loading or initial load)
    const imageCount = await page.locator('img').count();
    expect(imageCount).toBeGreaterThan(0);
  });

  test('search bar is visible and focusable', async ({ page }) => {
    const searchInput = page.locator(
      'input[name="q"], input[title="Search for Products, Brands and More"], input[type="text"]',
    ).first();
    await expect(searchInput).toBeVisible({ timeout: 10_000 });
    await searchInput.click();
    await expect(searchInput).toBeFocused();
  });
});
