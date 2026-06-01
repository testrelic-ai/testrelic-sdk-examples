# Maestro example — Wikipedia + `@testrelic/maestro-analytics`

YAML flows run against the **real Wikipedia Android app** (`org.wikipedia`), using the same APK path as the [Appium](../appium) example (see [mobile-apps/README.md](../mobile-apps/README.md)).

## Prerequisites

- **Node.js** >= 18
- **Maestro CLI** on your `PATH` so `maestro --version` works (the `testrelic-maestro` wrapper shells out to it). Options:
  - [Maestro Studio / installer](https://docs.maestro.dev/getting-started/installing-maestro) (Windows `.exe`), or
  - **Windows (CLI zip):** download [maestro.zip](https://github.com/mobile-dev-inc/Maestro/releases) for the current `cli-*` tag, unzip, then add the `maestro\bin` folder to `PATH` (for one PowerShell session: `$env:PATH = "$env:USERPROFILE\.maestro\cli-VERSION\maestro\bin;$env:PATH"`).
- **Android** device or emulator with `adb devices` showing the target
- **`../mobile-apps/wikipedia.apk`** — from repo root run `node mobile-apps/download-wikipedia-apk.mjs` if the file is missing (see [mobile-apps/README.md](../mobile-apps/README.md)), then install on the device:

  ```bash
  adb install -r ../mobile-apps/wikipedia.apk
  ```

For Wikipedia **Explore** content (same as [Appium](../appium)), keep the emulator **online** (airplane mode off, Wi‑Fi/data on). Example:

```bash
adb shell cmd connectivity airplane-mode disable
adb shell svc wifi enable
adb shell svc data enable
```

## Setup

```bash
cd maestro
npm install
```

## Run (TestRelic wrapper)

Runs Maestro on `./flows` and writes local reports under `./test-results/` (see [`@testrelic/maestro-analytics`](https://www.npmjs.com/package/@testrelic/maestro-analytics)). The `npm test` script loads the **repository root** `.env` and applies the same staging defaults as Playwright (**`TESTRELIC_STAGE_API_KEY` → `TESTRELIC_API_KEY`**, **`TESTRELIC_CLOUD_ENDPOINT` → `TESTRELIC_STAGE_CLOUD_ENDPOINT` or `https://stage.testrelic.ai/api/v1`**), then runs `testrelic-maestro`. See [`.env.example`](../.env.example).

```bash
npm test
```

To open the HTML report after the run, use the wrapper without `--no-open` (edit the `test` script in `package.json` to drop `--no-open`), or run:

```bash
npx testrelic-maestro test ./flows
```

### TestRelic cloud (optional)

Set **`TESTRELIC_API_KEY`** in your environment (do not commit keys). This example includes [`.testrelic/testrelic-config.json`](.testrelic/testrelic-config.json) with `apiKey` **`$TESTRELIC_API_KEY`** (resolved when the file is read), `upload: "both"`, and **`testrelic-repo.name`**: `maestro-wikipedia-examples`, aligned with the Playwright examples.

Priority (highest first): **`TESTRELIC_API_KEY`** / **`TESTRELIC_CLOUD_ENDPOINT`** env vars, then CLI flags (`--api-key`, `--endpoint`), then the config file. See [`@testrelic/maestro-analytics`](https://www.npmjs.com/package/@testrelic/maestro-analytics) for `cloud.upload` (`batch` | `realtime` | `both`), queue options, and the full reference.

## Flows

| File | Purpose |
|------|---------|
| `flows/wikipedia-launch.yaml` | Launch app, dismiss optional onboarding taps, wait for main search UI (`search_container`) |
| `flows/wikipedia-search-field.yaml` | Same setup, assert the main search container is visible |

If Wikimedia changes resource ids, update `wikipedia-search-field.yaml` or rely on `wikipedia-launch.yaml` only.
