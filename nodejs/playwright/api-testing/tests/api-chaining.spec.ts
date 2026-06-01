import { test, expect } from './fixtures';

test.describe('API Call Chaining — Data Flow Between Requests', { tag: ['@api'] }, () => {
  const BASE_URL = 'https://jsonplaceholder.typicode.com';

  test('create a post then read it back', async ({ request }) => {
    // Step 1: Create a new post
    const createResponse = await request.post(`${BASE_URL}/posts`, {
      data: {
        title: 'Chained Test Post',
        body: 'Created to demonstrate API call chaining',
        userId: 1,
      },
    });
    expect(createResponse.status()).toBe(201);
    const created = await createResponse.json();
    const createdId = created.id;
    expect(createdId).toBe(101);

    // Step 2: Read back using the created post's userId
    // (Using existing post ID 1 since JSONPlaceholder doesn't persist writes)
    const readResponse = await request.get(`${BASE_URL}/posts/1`);
    expect(readResponse.status()).toBe(200);
    const post = await readResponse.json();
    expect(post.userId).toBe(created.userId);
  });

  test('full CRUD lifecycle — create, read, update, verify, delete, confirm', async ({ request }) => {
    // Step 1: CREATE a post
    const createResponse = await request.post(`${BASE_URL}/posts`, {
      data: { title: 'Lifecycle Post', body: 'Will go through full CRUD', userId: 1 },
    });
    expect(createResponse.status()).toBe(201);
    const created = await createResponse.json();
    expect(created.id).toBe(101);

    // Step 2: READ the post (using existing ID since JSONPlaceholder simulates writes)
    const readResponse = await request.get(`${BASE_URL}/posts/1`);
    expect(readResponse.status()).toBe(200);

    // Step 3: UPDATE the post via PUT
    const updateResponse = await request.put(`${BASE_URL}/posts/1`, {
      data: { id: 1, title: 'Updated Lifecycle Post', body: 'Modified content', userId: 1 },
    });
    expect(updateResponse.status()).toBe(200);
    const updated = await updateResponse.json();
    expect(updated.title).toBe('Updated Lifecycle Post');

    // Step 4: VERIFY the update via GET
    const verifyResponse = await request.get(`${BASE_URL}/posts/1`);
    expect(verifyResponse.status()).toBe(200);

    // Step 5: DELETE the post
    const deleteResponse = await request.delete(`${BASE_URL}/posts/1`);
    expect(deleteResponse.status()).toBe(200);

    // Step 6: CONFIRM deletion — a non-existent ID returns 404
    const confirmResponse = await request.get(`${BASE_URL}/posts/99999`);
    expect(confirmResponse.status()).toBe(404);
  });

  test('cross-resource chain — user to posts to comments', async ({ request }) => {
    // Step 1: Get a user
    const userResponse = await request.get(`${BASE_URL}/users/1`);
    expect(userResponse.status()).toBe(200);
    const user = await userResponse.json();
    const userId = user.id;
    expect(userId).toBe(1);

    // Step 2: Get posts for that user (using userId from Step 1)
    const postsResponse = await request.get(`${BASE_URL}/posts?userId=${userId}`);
    expect(postsResponse.status()).toBe(200);
    const posts = await postsResponse.json();
    expect(posts.length).toBeGreaterThan(0);
    const firstPostId = posts[0].id;

    // Step 3: Get comments for the first post (using postId from Step 2)
    const commentsResponse = await request.get(`${BASE_URL}/posts/${firstPostId}/comments`);
    expect(commentsResponse.status()).toBe(200);
    const comments = await commentsResponse.json();
    expect(comments.length).toBeGreaterThan(0);
    expect(comments[0].postId).toBe(firstPostId);
  });
});
