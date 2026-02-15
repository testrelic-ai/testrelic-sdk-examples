/**
 * Configuration Options — TestRelic API Config Showcase
 *
 * This spec demonstrates features controlled by TestRelic reporter configuration.
 * The default playwright.config.ts uses standard settings. To see the effect of
 * different configurations, modify the reporter options:
 *
 * ── Disable request/response body capture ──
 *   captureRequestBody: false,
 *   captureResponseBody: false,
 *
 * ── Disable header capture ──
 *   captureRequestHeaders: false,
 *   captureResponseHeaders: false,
 *
 * ── Custom redaction lists (replace defaults) ──
 *   redactHeaders: ['authorization', 'x-api-key', 'x-custom-secret'],
 *   redactBodyFields: ['password', 'ssn', 'creditCard'],
 *
 * ── Disable all redaction ──
 *   redactHeaders: [],
 *   redactBodyFields: [],
 *
 * ── Filter which API URLs are tracked ──
 *   apiIncludeUrls: ['** /posts/**'],
 *   apiExcludeUrls: ['** /comments/**'],
 *
 * ── Disable API tracking entirely ──
 *   trackApiCalls: false,
 */

import { test, expect } from './fixtures';

test.describe('Configuration Options — TestRelic API Config', { tag: ['@api'] }, () => {
  const BASE_URL = 'https://jsonplaceholder.typicode.com';

  test('default redaction of sensitive headers — Authorization and X-Api-Key', async ({ request }) => {
    // The default config redacts: authorization, cookie, set-cookie, x-api-key
    // In the TestRelic report, these header values will appear as [REDACTED]
    const response = await request.get(`${BASE_URL}/posts/1`, {
      headers: {
        'Authorization': 'Bearer my-secret-token-12345',
        'X-Api-Key': 'sk_live_abc123def456',
      },
    });
    expect(response.status()).toBe(200);

    const post = await response.json();
    expect(post.id).toBe(1);
  });

  test('default redaction of sensitive body fields — password and token', async ({ request }) => {
    // The default config redacts body fields: password, secret, token, apiKey, api_key
    // In the TestRelic report, these field values will appear as [REDACTED]
    const response = await request.post(`${BASE_URL}/posts`, {
      data: {
        title: 'Config Demo Post',
        body: 'Demonstrating body field redaction',
        userId: 1,
        password: 'super-secret-password-123',
        token: 'refresh_token_xyz789',
        apiKey: 'ak_prod_secret_key',
      },
    });
    expect(response.status()).toBe(201);

    const created = await response.json();
    expect(created.id).toBe(101);
  });

  test('non-sensitive custom headers — visible in report', async ({ request }) => {
    // Custom headers that are NOT in the redaction list remain visible in the report
    const response = await request.get(`${BASE_URL}/posts/1`, {
      headers: {
        'X-Request-Id': 'req-abc-123-def-456',
        'X-Correlation-Id': 'corr-789-ghi-012',
        'Accept-Language': 'en-US',
      },
    });
    expect(response.status()).toBe(200);

    const post = await response.json();
    expect(post.id).toBe(1);
  });

  test('large response body capture — 100 posts array', async ({ request }) => {
    // The report captures the full response body regardless of size
    // With captureResponseBody: false, the body would be null in the report
    const response = await request.get(`${BASE_URL}/posts`);
    expect(response.status()).toBe(200);

    const posts = await response.json();
    expect(posts.length).toBe(100);
  });

  test('response time tracking — visible in report timeline', async ({ request }) => {
    // Every API call in the report includes responseTime in milliseconds
    // This is captured automatically by the API request tracker
    const response = await request.get(`${BASE_URL}/posts/1`);
    expect(response.status()).toBe(200);
    expect(response.ok()).toBeTruthy();
  });
});
