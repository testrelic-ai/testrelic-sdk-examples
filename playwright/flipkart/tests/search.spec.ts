import { test, expect } from '@testrelic/playwright-analytics/fixture';

test.describe('Flipkart Search & Product Navigation', { tag: ['@e2e'] }, () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://www.flipkart.com');
    await page.waitForLoadState('domcontentloaded');
    try {
      await page.locator('button:has-text("✕")').click({ timeout: 3_000 });
    } catch {
      // No popup
    }
  });

  test('searching for iPhone shows results', async ({ page }) => {
    const searchInput = page.locator(
      'input[name="q"], input[title="Search for Products, Brands and More"], input[type="text"]',
    ).first();
    await searchInput.fill('iPhone');
    await searchInput.press('Enter');
    await page.waitForLoadState('domcontentloaded');

    expect(page.url()).toContain('q=iPhone');

    // Verify search results rendered — product links contain "/p/"
    await expect(
      page.locator('a[href*="/p/"]').first(),
    ).toBeVisible({ timeout: 15_000 });
  });

  test('clicking an iPhone result opens the product page', async ({ page }) => {
    const searchInput = page.locator(
      'input[name="q"], input[title="Search for Products, Brands and More"], input[type="text"]',
    ).first();
    await searchInput.fill('iPhone');
    await searchInput.press('Enter');
    await page.waitForLoadState('domcontentloaded');

    // Wait for product links
    const productLink = page.locator('a[href*="/p/"]').first();
    await expect(productLink).toBeVisible({ timeout: 15_000 });

    // Extract href and navigate directly (avoids target="_blank" new tab,
    // keeps all navigations on the tracked fixture page for richer timeline)
    const href = await productLink.getAttribute('href');
    expect(href).toBeTruthy();
    const productUrl = href!.startsWith('http') ? href! : `https://www.flipkart.com${href}`;
    await page.goto(productUrl);
    await page.waitForLoadState('domcontentloaded');

    expect(page.url()).toContain('flipkart.com');
    // Wait for product page to render — verify meaningful content loaded
    await page.waitForLoadState('networkidle');
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
  });
});
