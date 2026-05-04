const path = require('node:path');
const { spawnSync } = require('node:child_process');

require('dotenv').config({
  path: path.resolve(__dirname, '..', '..', '.env'),
});

const DEFAULT_TESTRELIC_STAGE_CLOUD_ENDPOINT =
  'https://stage.testrelic.ai/api/v1';

function applyTestRelicStagingEnv() {
  const stageKey = (process.env.TESTRELIC_STAGE_API_KEY || '').trim();
  if (!stageKey) {
    return;
  }
  process.env.TESTRELIC_API_KEY = stageKey;
  const stageEndpoint = (process.env.TESTRELIC_STAGE_CLOUD_ENDPOINT || '').trim();
  process.env.TESTRELIC_CLOUD_ENDPOINT =
    stageEndpoint || DEFAULT_TESTRELIC_STAGE_CLOUD_ENDPOINT;
}
applyTestRelicStagingEnv();

const r = spawnSync(
  'npx',
  ['--no-install', 'testrelic-maestro', 'test', './flows', '--no-open'],
  {
    stdio: 'inherit',
    shell: true,
    cwd: path.resolve(__dirname, '..'),
    env: process.env,
  },
);

process.exit(r.status === null ? 1 : r.status);
