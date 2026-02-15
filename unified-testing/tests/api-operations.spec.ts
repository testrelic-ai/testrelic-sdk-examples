/**
 * API Operations Tests — API-only tests using the `request` fixture.
 *
 * These tests demonstrate TestRelic's API call tracking within a unified
 * project that also has browser tests. The `request` fixture is available
 * alongside `page` from the same testRelicFixture.
 */
import { test, expect } from '@testrelic/playwright-analytics/fixture';

const API_BASE = 'https://jsonplaceholder.typicode.com';

test.describe('API Operations', { tag: ['@api'] }, () => {
  test('GET — fetch all posts', async ({ request }) => {
    const response = await request.get(`${API_BASE}/posts`);
    expect(response.status()).toBe(200);

    const posts = await response.json();
    expect(posts).toBeInstanceOf(Array);
    expect(posts.length).toBe(100);
  });

  test('POST — create a new post', async ({ request }) => {
    const response = await request.post(`${API_BASE}/posts`, {
      data: {
        title: 'Unified Testing Example',
        body: 'Demonstrating API tests alongside E2E tests',
        userId: 1,
      },
    });
    expect(response.status()).toBe(201);

    const created = await response.json();
    expect(created.id).toBe(101);
    expect(created.title).toBe('Unified Testing Example');
  });

  test('PUT — update a post', async ({ request }) => {
    const response = await request.put(`${API_BASE}/posts/1`, {
      data: {
        id: 1,
        title: 'Updated via Unified Test',
        body: 'Full resource replacement',
        userId: 1,
      },
    });
    expect(response.status()).toBe(200);

    const updated = await response.json();
    expect(updated.title).toBe('Updated via Unified Test');
  });

  test('DELETE — remove a post', async ({ request }) => {
    const response = await request.delete(`${API_BASE}/posts/1`);
    expect(response.status()).toBe(200);
  });

  test('API chaining — create then read back', async ({ request }) => {
    // Step 1: Create a new post
    const createResponse = await request.post(`${API_BASE}/posts`, {
      data: { title: 'Chained Test', body: 'Testing data flow', userId: 1 },
    });
    expect(createResponse.status()).toBe(201);
    const created = await createResponse.json();
    expect(created.id).toBeDefined();

    // Step 2: Read back an existing post (JSONPlaceholder doesn't persist)
    const readResponse = await request.get(`${API_BASE}/posts/1`);
    expect(readResponse.status()).toBe(200);
    const post = await readResponse.json();
    expect(post.id).toBe(1);
  });
});
