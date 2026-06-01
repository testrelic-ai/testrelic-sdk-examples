import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import dotenv from 'dotenv';
import { TestRelicService } from '@testrelic/appium-analytics/service';
import { TestRelicReporter } from '@testrelic/appium-analytics';

import { applyTestRelicStagingEnv } from '../scripts/apply-testrelic-staging-env.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, '../.env') });
applyTestRelicStagingEnv();
const apkPath = path.join(__dirname, '..', 'mobile-apps', 'swaglabs.apk');
const REPORT_DIR = path.join(__dirname, 'test-results');

if (!fs.existsSync(apkPath)) {
  throw new Error(
    `Missing APK at ${apkPath}. Download from https://github.com/saucelabs/sample-app-mobile/releases (Android.SauceLabs.Mobile.Sample.app.*.apk).`,
  );
}

async function onComplete() {
  try {
    await TestRelicReporter.finalize(process.cwd());
  } catch (err) {
    process.stderr.write(`[TestRelic] Cloud finalization failed: ${err}\n`);
  }
}

const testRelicCloud = {
  apiKey: process.env.TESTRELIC_API_KEY,
  upload: 'both' as const,
  uploadArtifacts: true,
  artifactMaxSizeMb: 50,
  timeout: 60_000,
};

export const config = {
  runner: 'local',
  hostname: '127.0.0.1',
  port: 4723,
  path: '/',
  connectionRetryTimeout: 300_000,
  specs: ['./tests/**/*.ts'],
  maxInstances: 1,
  capabilities: [
    {
      platformName: 'Android',
      'appium:deviceName': 'Android',
      'appium:automationName': 'UiAutomator2',
      'appium:app': apkPath,
      'appium:appPackage': 'com.swaglabsmobileapp',
      'appium:appActivity': 'com.swaglabsmobileapp.SplashActivity',
      'appium:autoGrantPermissions': true,
      // Avoid full reinstall / clear on every session (faster and more stable on emulators)
      'appium:noReset': true,
      // Emulator adb can exceed default 20s during session teardown (hidden API policy reset, etc.)
      'appium:adbExecTimeout': 120_000,
    },
  ],
  services: [
    ['appium', {}],
    [
      TestRelicService,
      {
        outputPath: REPORT_DIR,
        includeDeviceLogs: true,
        includeNetworkLogs: true,
        includeConsoleLogs: true,
        includeCommands: true,
        includeAssertions: true,
        includeScreenshots: true,
        screenshotOnEvery: 'test' as const,
        includeVideoRecording: true,
      },
    ],
  ],
  framework: 'mocha',
  reporters: [
    'spec',
    [
      TestRelicReporter,
      {
        outputPath: path.join(REPORT_DIR, 'report.json'),
        htmlReportPath: path.join(REPORT_DIR, 'report.html'),
        openReport: false,
        cloud: testRelicCloud,
      },
    ],
  ],
  mochaOpts: {
    ui: 'bdd',
    timeout: 120_000,
  },
  onComplete,
};
