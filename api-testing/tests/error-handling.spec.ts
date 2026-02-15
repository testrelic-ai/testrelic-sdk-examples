import { test, expect } from './fixtures';

test.describe('Error Handling and Edge Cases', { tag: ['@api'] }, () => {
  const BASE_URL = 'https://jsonplaceholder.typicode.com';

  test('404 not found — requesting a non-existent resource', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/posts/999999`);
    expect(response.status()).toBe(404);
  });

  test('invalid endpoint — requesting a path that does not exist', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/nonexistent-endpoint`);
    expect(response.status()).toBe(404);
  });

  test('empty body POST — server accepts minimal data', async ({ request }) => {
    // JSONPlaceholder accepts any data and returns it with an ID
    const response = await request.post(`${BASE_URL}/posts`, {
      data: {},
    });
    expect(response.status()).toBe(201);

    const body = await response.json();
    expect(body.id).toBeDefined();
  });

  test('query parameter filtering — non-existent user returns empty array', async ({ request }) => {
    // Filtering posts by a userId that doesn't exist returns an empty array
    const response = await request.get(`${BASE_URL}/posts?userId=99999`);
    expect(response.status()).toBe(200);

    const posts = await response.json();
    expect(posts).toBeInstanceOf(Array);
    expect(posts.length).toBe(0);
  });

  test('unicode and special characters in request body', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/posts`, {
      data: {
        title: 'Unicode Test: \u00e9\u00e0\u00fc\u00f1 \u4f60\u597d \ud83d\ude80\ud83c\udf1f',
        body: 'Special chars: <>&"\' and newlines\nand\ttabs',
        userId: 1,
      },
    });
    expect(response.status()).toBe(201);

    const created = await response.json();
    expect(created.title).toContain('\u00e9\u00e0\u00fc\u00f1');
    expect(created.title).toContain('\u4f60\u597d');
  });
});
