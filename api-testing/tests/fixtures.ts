import { test as base } from '@playwright/test';
import { testRelicApiFixture } from '@testrelic/playwright-analytics/api-fixture';
import { expect } from '@testrelic/playwright-analytics/fixture';

export const test = base.extend(testRelicApiFixture);
export { expect };
