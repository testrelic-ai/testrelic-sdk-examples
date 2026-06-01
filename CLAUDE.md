# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A polyglot examples monorepo demonstrating the TestRelic SDK reporters across three test stacks. Each subtree is a standalone, independently-installable example project — there is **no root `package.json`**, no workspace/monorepo tooling, and no shared lint/test runner. Workflows are coordinated via the top-level `Makefile`.

| Area | Stack | Reporter package |
|------|-------|------------------|
| `playwright/<example>/` | Playwright Test | `@testrelic/playwright-analytics` |
| `appium/` | WebdriverIO + Appium 2 (Mocha) | `@testrelic/appium-analytics` (`TestRelicService` + `TestRelicReporter`) |
| `maestro/` | Maestro YAML flows via `testrelic-maestro` wrapper | `@testrelic/maestro-analytics` |

`mobile-apps/` holds the shared Wikipedia APK (gitignored) used by both `appium/` and `maestro/`. `scripts/apply-testrelic-staging-env.mjs` is the shared cross-stack env helper.

## Commands

### Per-example (cd into the example, then):
- Playwright examples: `npm install && npx playwright test` (browser examples additionally need `npx playwright install chromium`)
- Appium: `npm install && npx appium driver install uiautomator2 && npm test`
- Maestro: `npm install && npm test` (runs `testrelic-maestro test ./flows --no-open`)

### Via Makefile (from repo root, bash only — see Windows note below):
- `make example-api-testing | example-wikipedia | example-flipkart | example-google | example-amazon | example-unified-testing`
- `make example-appium | example-maestro`
- `make example-mobile-apps-download` — fetches `mobile-apps/wikipedia.apk` from F-Droid
- `make examples` runs all Playwright examples; `make examples-e2e` skips the API-only one
- `make help` lists targets

### Running a single Playwright test
From an example dir: `npx playwright test tests/<file>.spec.ts` (optionally `-g "<title pattern>"`, `--workers=1`, `--reporter=list`). The TestRelic reporter is always wired via `playwright.config.ts`.

### Windows note
`Makefile` targets use bash-style `cd && …` chains and won't run from PowerShell. Use **Git Bash** or **WSL**, or invoke the underlying `npm`/`npx` commands directly from each example directory.

## Cross-cutting architecture

### .env lives at the repo root
Every example loads `../../.env` (Playwright/Maestro) or `../.env` (Appium) via `dotenv` **before** the reporter reads `process.env`. New VS Code/Cursor terminals also pick it up via `.vscode/settings.json`. There is no per-example `.env`.

### Staging-vs-prod env mirroring (critical)
`@testrelic/core` merges cloud config with `process.env` **last**, so `TESTRELIC_API_KEY` and `TESTRELIC_CLOUD_ENDPOINT` override both `playwright.config.ts`/`wdio.conf.ts` and the per-example `.testrelic/testrelic-config.json`. To support a staging key coexisting with a prod key in the same `.env`, each entrypoint calls `applyTestRelicStagingEnv()` (`scripts/apply-testrelic-staging-env.mjs`) immediately after `dotenv.config()`. The helper:

1. If `TESTRELIC_STAGE_API_KEY` is non-empty, copies it onto `TESTRELIC_API_KEY` (overwriting any prod key for this process).
2. Sets `TESTRELIC_CLOUD_ENDPOINT` to `TESTRELIC_STAGE_CLOUD_ENDPOINT`, or defaults to `https://stage.testrelic.ai/api/v1`.

The Maestro example reimplements this logic inline in `maestro/scripts/run-tests.cjs` (CJS context, can't import the ESM helper) — keep the two copies in sync.

### Per-example `.testrelic/testrelic-config.json`
Each example commits a config with `cloud.apiKey: "$TESTRELIC_API_KEY"` (resolved at read-time), `cloud.endpoint: https://platform.testrelic.ai/api/v1`, and a distinct `testrelic-repo.name` (e.g. `playwright-api-testing`, `appium-wikipedia-examples`, `maestro-wikipedia-examples`) so cloud runs show up under separate projects. The `endpoint` in this file is the **prod** default — staging overrides come from env vars per above.

### Mobile examples share one APK
Both `appium/wdio.conf.ts` and the Maestro flows expect `mobile-apps/wikipedia.apk` (F-Droid `org.wikipedia` build, downloaded via `mobile-apps/download-wikipedia-apk.mjs`). The Appium config asserts the file exists and pins `appium:appActivity: org.wikipedia.DefaultIcon` to avoid "Intent matches multiple activities" on this build. It also sets `noReset: true` and a 120s `adbExecTimeout` for emulator stability — be cautious about changing these.

### Reporter wiring lives in config, not test code
Tests import fixtures from `@testrelic/playwright-analytics/fixture` (Playwright) or use plain WebdriverIO/Mocha (Appium); none of the cloud/upload setup is in test files. Reporter options (`outputPath`, `includeStackTrace`, `includeCodeSnippets`, `includeNetworkStats`, `cloud.{upload,uploadArtifacts,artifactMaxSizeMb,timeout}`) are all set in `playwright.config.ts` / `wdio.conf.ts`.

## TestRelic MCP (Cursor)

`.cursor/mcp.json` registers `@testrelic/mcp@3.0.0` with `--caps core,coverage,creation,healing,impact`. Only `tr_*` tools in those capability groups are available; tools in `triage`, `signals`, or `devtools` require extending `--caps` (or `TESTRELIC_MCP_CAPS`) and restarting the MCP host. Auth flows through `TESTRELIC_MCP_TOKEN` or `npx -y @testrelic/mcp@3.0.0 login` — don't print `.env` contents. See `.cursor/skills/testrelic-mcp/SKILL.md` for the tool catalog and typical flows.
