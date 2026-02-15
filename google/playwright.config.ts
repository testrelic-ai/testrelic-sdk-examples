import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  retries: 1,
  workers: 1,
  use: {
    headless: true,
    viewport: { width: 1280, height: 720 },
    actionTimeout: 10_000,
    navigationTimeout: 15_000,
    screenshot: 'on',
    video: 'on',
  },
  reporter: [
    ['list'],
    ['@testrelic/playwright-analytics', {
      outputPath: './test-results/analytics-timeline.json',
      includeStackTrace: true,
      includeCodeSnippets: true,
      includeNetworkStats: true,
      metadata: { example: 'google' },
    }],
  ],
});
