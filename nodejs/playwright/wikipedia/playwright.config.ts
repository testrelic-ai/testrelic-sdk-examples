import path from 'node:path';
import { fileURLToPath } from 'node:url';

import dotenv from 'dotenv';
import { defineConfig } from '@playwright/test';

import { applyTestRelicStagingEnv } from '../../scripts/apply-testrelic-staging-env.mjs';

dotenv.config({
  path: path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../.env'),
});
applyTestRelicStagingEnv();

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  retries: 0,
  workers: 1,
  use: {
    headless: true,
    viewport: { width: 1280, height: 720 },
    actionTimeout: 10_000,
    navigationTimeout: 15_000,
    trace: 'on',
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
      metadata: { example: 'wikipedia' },
      cloud: {
        apiKey: process.env.TESTRELIC_API_KEY,
        upload: 'both',
        uploadArtifacts: true,
        artifactMaxSizeMb: 10,
        timeout: 30_000,
      },
    }],
  ],
});
