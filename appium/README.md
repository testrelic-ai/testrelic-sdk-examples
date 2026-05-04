# Appium example — Wikipedia (WebdriverIO + Appium 2)

End-to-end smoke tests against the **real Wikipedia Android app**, using the same APK as [Maestro](../maestro) (see [mobile-apps/README.md](../mobile-apps/README.md)). Runs with [`@testrelic/appium-analytics`](https://www.npmjs.com/package/@testrelic/appium-analytics) (`TestRelicService` + `TestRelicReporter`) for local HTML/JSON reports and optional **TestRelic cloud** upload.

## Prerequisites

- **Node.js** >= 18
- **Android SDK** / platform-tools on your `PATH` (`adb devices` works)
- **JDK** 17+ (required by Appium 2)
- Android **emulator running** or a physical device in developer mode
- **`../mobile-apps/wikipedia.apk`** present — from repo root run `node mobile-apps/download-wikipedia-apk.mjs` (F-Droid production `org.wikipedia`), or see [mobile-apps/README.md](../mobile-apps/README.md)

### One-time: UiAutomator2 driver

After `npm install`:

```bash
npx appium driver install uiautomator2
```

## Setup

```bash
cd appium
npm install
npx appium driver install uiautomator2
```

## Run

Starts Appium via `@wdio/appium-service` and runs specs. Reports are written under `./test-results/` (`report.json`, `report.html`).

```bash
npm test
```

If port `4723` is busy, stop other Appium instances or adjust `wdio.conf.ts`.

### TestRelic cloud (optional)

Set **`TESTRELIC_API_KEY`** in your environment for uploads (do not commit keys), or put it in the **repository root** `.env` — [`wdio.conf.ts`](wdio.conf.ts) loads that file with `dotenv` before reading `process.env`. If **`TESTRELIC_STAGE_API_KEY`** is set, it is copied onto **`TESTRELIC_API_KEY`** and **`TESTRELIC_CLOUD_ENDPOINT`** is set from **`TESTRELIC_STAGE_CLOUD_ENDPOINT`** or defaulted to **`https://stage.testrelic.ai/api/v1`** (same helper as Playwright; see [`.env.example`](../.env.example)). The config passes a `cloud` block to the reporter (`upload: 'both'`, `uploadArtifacts`, `artifactMaxSizeMb`, `timeout`) using `process.env.TESTRELIC_API_KEY`, merged with [`.testrelic/testrelic-config.json`](.testrelic/testrelic-config.json) (`testrelic-repo.name`: `appium-wikipedia-examples`). Env vars override the file per the [package readme](https://www.npmjs.com/package/@testrelic/appium-analytics). **`onComplete`** calls `TestRelicReporter.finalize(process.cwd())` so batch cloud upload completes after the run.

You can also set **`TESTRELIC_CLOUD_ENDPOINT`** or **`TESTRELIC_UPLOAD_STRATEGY`** (`batch` | `realtime` | `both`) in CI.

### Emulator checklist (Windows / macOS / Linux)

1. Start an AVD (e.g. Android Studio **Device Manager**, or `emulator -avd <Your_Avd_Name>`).
2. Install the Wikipedia APK once (idempotent):

   ```bash
   adb install -r ../mobile-apps/wikipedia.apk
   ```

3. From `appium/`, run `npm test`.

If Wikipedia shows **offline** / “could not load” on the **Explore** feed, the emulator may have had **airplane mode** on or no route to the internet. From the host (with `adb` on your `PATH`):

```bash
adb shell cmd connectivity airplane-mode disable
adb shell svc wifi enable
adb shell svc data enable
adb shell settings put global private_dns_mode off
```

Then reopen Wikipedia or rerun `npm test`.

[`wdio.conf.ts`](wdio.conf.ts) sets **`appium:appActivity`** to **`org.wikipedia.DefaultIcon`** (the resolved launcher activity for this build) so Appium does not hit *“Intent matches multiple activities”*. It also uses **`appium:noReset`: true** and a higher **`appium:adbExecTimeout`** so repeat runs and emulator teardown stay stable. Reinstall the APK or clear app data if you need a completely fresh Wikipedia state.

## Tests

| File | What it checks |
|------|----------------|
| `tests/wikipedia.spec.ts` | Opens Wikipedia, dismisses common onboarding buttons if present, asserts toolbar text or search container is visible |

CLI helpers from the same package: `npx testrelic-appium serve ./test-results`, `merge`, etc. — see the npm readme.
