import { test, expect } from '@testrelic/playwright-analytics/fixture';

test.describe('Wikipedia Navigation', { tag: ['@e2e'] }, () => {
  test('clicking an article link navigates to new page', async ({ page }) => {
    await page.goto('https://en.wikipedia.org/wiki/Software_testing');
    await page.waitForLoadState('domcontentloaded');
    const link = page.locator('a[href="/wiki/Unit_testing"]').first();
    await link.click();
    await page.waitForLoadState('domcontentloaded');
    expect(page.url()).toContain('Unit_testing');
  });

  test('back navigation returns to previous page', async ({ page }) => {
    await page.goto('https://en.wikipedia.org/wiki/Main_Page');
    await page.waitForLoadState('domcontentloaded');
    await page.goto('https://en.wikipedia.org/wiki/Node.js');
    await page.waitForLoadState('domcontentloaded');
    await page.goBack();
    await page.waitForLoadState('domcontentloaded');
    expect(page.url()).toContain('Main_Page');
  });

  test('forward navigation after going back', async ({ page }) => {
    await page.goto('https://en.wikipedia.org/wiki/Main_Page');
    await page.waitForLoadState('domcontentloaded');
    await page.goto('https://en.wikipedia.org/wiki/Node.js');
    await page.waitForLoadState('domcontentloaded');
    await page.goBack();
    await page.waitForLoadState('domcontentloaded');
    await page.goForward();
    await page.waitForLoadState('domcontentloaded');
    expect(page.url()).toContain('Node.js');
  });
});
