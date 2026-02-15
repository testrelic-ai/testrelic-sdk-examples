/**
 * Unified Workflow Tests — Tests that use BOTH `page` and `request` fixtures.
 *
 * These tests demonstrate the key value of TestRelic's unified fixture:
 * combining browser navigation with API calls in a single test, so the
 * TestRelic report shows both navigation timeline AND API call details
 * for the same test.
 */
import { test, expect } from '@testrelic/playwright-analytics/fixture';

const API_BASE = 'https://jsonplaceholder.typicode.com';

test.describe('Unified Workflow — Browser + API', { tag: ['@e2e', '@api'] }, () => {
  test('verify API data matches what the browser renders', async ({ page, request }) => {
    // Step 1: Fetch user data via API
    const apiResponse = await request.get(`${API_BASE}/users/1`);
    expect(apiResponse.status()).toBe(200);
    const user = await apiResponse.json();
    expect(user.name).toBe('Leanne Graham');

    // Step 2: Navigate to a page in the browser
    await page.goto('https://en.wikipedia.org/wiki/Main_Page');
    await expect(page).toHaveTitle(/Wikipedia/);

    // The TestRelic report will show both the API call AND the browser
    // navigation in the same test's timeline, giving full visibility
    // into the test's behavior.
  });

  test('API setup followed by browser verification', async ({ page, request }) => {
    // Step 1: Use API to get data that would drive UI testing
    const postsResponse = await request.get(`${API_BASE}/posts?userId=1`);
    expect(postsResponse.status()).toBe(200);
    const posts = await postsResponse.json();
    expect(posts.length).toBe(10);

    // Step 2: Navigate in the browser (simulating verifying the UI shows this data)
    await page.goto('https://en.wikipedia.org/wiki/Software_testing');
    await expect(page).toHaveTitle(/Software testing/);

    // Step 3: Make another API call for additional context
    const userResponse = await request.get(`${API_BASE}/users/1`);
    expect(userResponse.status()).toBe(200);
    const userData = await userResponse.json();
    expect(userData.username).toBe('Bret');
  });

  test('browser navigation with API health check', async ({ page, request }) => {
    // Step 1: API health check before browser test
    const healthCheck = await request.get(`${API_BASE}/posts/1`);
    expect(healthCheck.status()).toBe(200);

    // Step 2: Browser navigation and interaction
    await page.goto('https://en.wikipedia.org/wiki/Main_Page');
    const searchInput = page.locator('#searchInput').first();
    await searchInput.fill('API');
    await searchInput.press('Enter');
    await page.waitForLoadState('domcontentloaded');

    // Step 3: Post-navigation API call
    const postNavApiCall = await request.get(`${API_BASE}/users`);
    expect(postNavApiCall.status()).toBe(200);
    const users = await postNavApiCall.json();
    expect(users.length).toBe(10);
  });

  test('CRUD via API then verify navigation still works', async ({ page, request }) => {
    // Step 1: Full CRUD lifecycle via API
    const createResponse = await request.post(`${API_BASE}/posts`, {
      data: { title: 'Created in unified test', body: 'Testing both fixtures', userId: 1 },
    });
    expect(createResponse.status()).toBe(201);

    const updateResponse = await request.patch(`${API_BASE}/posts/1`, {
      data: { title: 'Updated in unified test' },
    });
    expect(updateResponse.status()).toBe(200);

    const deleteResponse = await request.delete(`${API_BASE}/posts/1`);
    expect(deleteResponse.status()).toBe(200);

    // Step 2: Browser navigation after API operations
    await page.goto('https://en.wikipedia.org/wiki/Main_Page');
    await expect(page).toHaveTitle(/Wikipedia/);
  });
});
