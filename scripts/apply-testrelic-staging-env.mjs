/**
 * @testrelic/core merges cloud config with process.env last — both
 * TESTRELIC_API_KEY and TESTRELIC_CLOUD_ENDPOINT override file + reporter options.
 * When using staging credentials, mirror them onto those names before reporters run.
 */
export const DEFAULT_TESTRELIC_STAGE_CLOUD_ENDPOINT =
  'https://stage.testrelic.ai/api/v1';

export function applyTestRelicStagingEnv() {
  const stageKey = (process.env.TESTRELIC_STAGE_API_KEY || '').trim();
  if (!stageKey) {
    return;
  }

  process.env.TESTRELIC_API_KEY = stageKey;

  const stageEndpoint = (process.env.TESTRELIC_STAGE_CLOUD_ENDPOINT || '').trim();
  process.env.TESTRELIC_CLOUD_ENDPOINT =
    stageEndpoint || DEFAULT_TESTRELIC_STAGE_CLOUD_ENDPOINT;
}
