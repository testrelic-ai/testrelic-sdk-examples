import { test, expect } from './fixtures';

test.describe('CRUD Operations — HTTP Methods', { tag: ['@api'] }, () => {
  const BASE_URL = 'https://jsonplaceholder.typicode.com';

  test('GET all posts — fetches a collection of resources', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/posts`);
    expect(response.status()).toBe(200);

    const posts = await response.json();
    expect(posts).toBeInstanceOf(Array);
    expect(posts.length).toBe(100);
  });

  test('GET single post — fetches a resource by ID', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/posts/1`);
    expect(response.status()).toBe(200);

    const post = await response.json();
    expect(post.id).toBe(1);
    expect(post.title).toBeDefined();
    expect(post.body).toBeDefined();
    expect(post.userId).toBe(1);
  });

  test('POST — creates a new resource', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/posts`, {
      data: {
        title: 'TestRelic API Testing',
        body: 'Demonstrating POST request tracking with TestRelic',
        userId: 1,
      },
    });
    expect(response.status()).toBe(201);

    const created = await response.json();
    expect(created.id).toBe(101);
    expect(created.title).toBe('TestRelic API Testing');
    expect(created.userId).toBe(1);
  });

  test('PUT — full update of a resource', async ({ request }) => {
    const response = await request.put(`${BASE_URL}/posts/1`, {
      data: {
        id: 1,
        title: 'Updated Title via PUT',
        body: 'Completely replaced body content',
        userId: 1,
      },
    });
    expect(response.status()).toBe(200);

    const updated = await response.json();
    expect(updated.title).toBe('Updated Title via PUT');
    expect(updated.body).toBe('Completely replaced body content');
  });

  test('PATCH — partial update of a resource', async ({ request }) => {
    const response = await request.patch(`${BASE_URL}/posts/1`, {
      data: {
        title: 'Patched Title Only',
      },
    });
    expect(response.status()).toBe(200);

    const patched = await response.json();
    expect(patched.title).toBe('Patched Title Only');
    expect(patched.id).toBe(1);
  });

  test('DELETE — removes a resource', async ({ request }) => {
    const response = await request.delete(`${BASE_URL}/posts/1`);
    expect(response.status()).toBe(200);
  });
});
