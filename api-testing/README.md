# API Testing Example — @testrelic/playwright-analytics

Pure API tests against [JSONPlaceholder](https://jsonplaceholder.typicode.com) demonstrating HTTP methods, request chaining, response assertions, configuration options, and error handling — all tracked by TestRelic without launching a browser.

## Setup

```bash
npm install
```

No browser installation needed — this example uses only the Playwright API request client.

## Run

```bash
npx playwright test
```

The analytics report will be written to `./test-results/analytics-timeline.json`.

## Tests

| File | What it covers |
|------|----------------|
| `crud-operations.spec.ts` | GET, POST, PUT, PATCH, DELETE against /posts |
| `api-chaining.spec.ts` | Multi-step workflows with data flowing between requests |
| `response-assertions.spec.ts` | Status codes, body fields, structure, arrays, headers, failing assertions |
| `config-options.spec.ts` | Header/body redaction, custom headers, large responses, response time |
| `error-handling.spec.ts` | 404 responses, invalid endpoints, empty bodies, unicode characters |

## Configuration Variants

The default `playwright.config.ts` uses standard settings. Modify the reporter options to see different behaviors:

### Disable request/response body capture

```typescript
['@testrelic/playwright-analytics', {
  outputPath: './test-results/analytics-timeline.json',
  captureRequestBody: false,
  captureResponseBody: false,
}]
```

### Custom redaction lists

```typescript
['@testrelic/playwright-analytics', {
  outputPath: './test-results/analytics-timeline.json',
  redactHeaders: ['authorization', 'x-api-key', 'x-custom-secret'],
  redactBodyFields: ['password', 'ssn', 'creditCard'],
}]
```

### Disable all redaction

```typescript
['@testrelic/playwright-analytics', {
  outputPath: './test-results/analytics-timeline.json',
  redactHeaders: [],
  redactBodyFields: [],
}]
```

### API URL filtering

```typescript
['@testrelic/playwright-analytics', {
  outputPath: './test-results/analytics-timeline.json',
  apiIncludeUrls: ['**/posts/**'],
  apiExcludeUrls: ['**/comments/**'],
}]
```

### Disable API tracking entirely

```typescript
['@testrelic/playwright-analytics', {
  outputPath: './test-results/analytics-timeline.json',
  trackApiCalls: false,
}]
```

## Notes

- JSONPlaceholder simulates write operations: POST returns a new ID (always 101 for /posts), PUT/PATCH return updated data, DELETE returns an empty object. Data is never actually persisted on the server.
- The `response-assertions.spec.ts` includes one intentionally failing test (marked with `test.fail()`) to demonstrate how TestRelic captures failed assertions with expected vs actual values.
- All tests use the `@api` tag for correct test type classification in the report.

## Features Demonstrated

- **HTTP methods**: GET, POST, PUT, PATCH, DELETE
- **API call chaining**: Data from one response used in subsequent requests
- **Response assertions**: Status codes, body fields, nested objects, arrays, headers
- **Default redaction**: Authorization/cookie headers and password/token body fields
- **Custom headers**: Non-redacted headers visible in report
- **Large responses**: Full 100-item array captured
- **Response times**: Millisecond-precision timing per call
- **Error responses**: 404 status codes and error bodies
- **Edge cases**: Empty bodies, unicode characters, query parameter filtering
- **Expected failures**: `test.fail()` for assertion failure demonstration
