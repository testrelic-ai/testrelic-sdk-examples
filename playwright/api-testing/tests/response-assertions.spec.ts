import { test, expect } from './fixtures';

test.describe('Response Assertions — Validation Patterns', { tag: ['@api'] }, () => {
  const BASE_URL = 'https://jsonplaceholder.typicode.com';

  test('status code assertions — verifying HTTP status codes', async ({ request }) => {
    // 200 OK for existing resource
    const okResponse = await request.get(`${BASE_URL}/posts/1`);
    expect(okResponse.status()).toBe(200);

    // 404 Not Found for missing resource
    const notFoundResponse = await request.get(`${BASE_URL}/posts/99999`);
    expect(notFoundResponse.status()).toBe(404);

    // 201 Created for POST
    const createResponse = await request.post(`${BASE_URL}/posts`, {
      data: { title: 'Status Test', body: 'Testing', userId: 1 },
    });
    expect(createResponse.status()).toBe(201);
  });

  test('response body field assertions — checking specific values', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/users/1`);
    expect(response.status()).toBe(200);

    const user = await response.json();

    // Exact value assertions
    expect(user.id).toBe(1);
    expect(user.name).toBe('Leanne Graham');
    expect(user.username).toBe('Bret');
    expect(user.email).toBe('Sincere@april.biz');
  });

  test('response body structure assertions — verifying shape', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/users/1`);
    expect(response.status()).toBe(200);

    const user = await response.json();

    // Field existence
    expect(user.name).toBeDefined();
    expect(user.email).toBeDefined();
    expect(user.address).toBeDefined();
    expect(user.company).toBeDefined();

    // Nested structure
    expect(user.address.street).toBeDefined();
    expect(user.address.city).toBe('Gwenborough');
    expect(user.address.zipcode).toBeDefined();
    expect(user.address.geo).toBeDefined();
    expect(user.address.geo.lat).toBeDefined();
    expect(user.address.geo.lng).toBeDefined();
  });

  test('array assertions — validating collections', async ({ request }) => {
    // All posts
    const allPostsResponse = await request.get(`${BASE_URL}/posts`);
    expect(allPostsResponse.status()).toBe(200);
    const allPosts = await allPostsResponse.json();
    expect(allPosts.length).toBe(100);

    // Filtered posts for a specific user
    const userPostsResponse = await request.get(`${BASE_URL}/posts?userId=1`);
    expect(userPostsResponse.status()).toBe(200);
    const userPosts = await userPostsResponse.json();
    expect(userPosts.length).toBe(10);

    // Each post has required fields
    for (const post of userPosts) {
      expect(post.id).toBeDefined();
      expect(post.title).toBeDefined();
      expect(post.body).toBeDefined();
      expect(post.userId).toBe(1);
    }
  });

  test('response header assertions — checking HTTP headers', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/posts/1`);
    expect(response.status()).toBe(200);

    const headers = response.headers();

    // Content-Type header
    expect(headers['content-type']).toContain('application/json');

    // Standard response headers
    expect(headers['cache-control']).toBeDefined();
  });

  test('intentionally failing assertion — demonstrates report capture of failures', async ({ request }) => {
    // This test is marked as expected-to-fail to demonstrate how TestRelic
    // captures failed assertions with expected vs actual values in the report
    test.fail();

    const response = await request.get(`${BASE_URL}/posts`);
    expect(response.status()).toBe(200);

    const posts = await response.json();
    // This assertion will fail: there are 100 posts, not 999
    expect(posts.length).toBe(999);
  });
});
