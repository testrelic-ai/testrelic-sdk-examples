# Shared mobile app binaries

Real app packages used by [Appium](../appium) and [Maestro](../maestro). Large binaries stay **out of git** (see root `.gitignore`); populate this folder locally with the command below.

## Wikipedia Android — `wikipedia.apk` (production `org.wikipedia`)

### Put the APK here (recommended)

From this directory:

```bash
cd mobile-apps
npm install   # no dependencies; optional — only needed for the npm script name
npm run download
```

Or directly:

```bash
node mobile-apps/download-wikipedia-apk.mjs
```

The script reads [F-Droid’s `org.wikipedia` metadata](https://f-droid.org/api/v1/packages/org.wikipedia) for `suggestedVersionCode`, then downloads the matching APK from `https://f-droid.org/repo/org.wikipedia_<versionCode>.apk` and saves it as **`mobile-apps/wikipedia.apk`** (same application id **`org.wikipedia`** as in the Maestro flows and Appium smoke test).

Then install on a device or emulator:

```bash
adb install -r mobile-apps/wikipedia.apk
```

### Manual download

Alternatively, open [Wikipedia on F-Droid](https://f-droid.org/en/packages/org.wikipedia/) or [Wikimedia GitHub releases](https://github.com/wikimedia/apps-android-wikipedia/releases), download a universal **APK**, and save it as **`wikipedia.apk`** in this folder.

| Platform | File | Bundle / application id |
|----------|------|-------------------------|
| Android | `mobile-apps/wikipedia.apk` | `org.wikipedia` |
| iOS | See [Wikipedia iOS](#wikipedia-ios-ipa-app-bundle-simulator) | Bundle id from your build or the App Store build you automate |

## Wikipedia iOS (ipa, app bundle, simulator)

### Why there is no “download `.ipa`” script (unlike Android)

- **Android:** F-Droid publishes a direct **APK** URL for `org.wikipedia`, so this repo can automate `wikipedia.apk`.
- **iOS:** There is **no** equivalent public, legal, stable URL to pull the same app the App Store ships as an **`.ipa`** for everyone. The [Wikipedia iOS](https://github.com/wikimedia/wikipedia-ios) GitHub **releases do not attach `.ipa` binaries** (they are source/tag releases only). Apple’s model is install via App Store, TestFlight, or **your own** signed build output.

So **`.ipa` files are optional local artifacts** you create or export; place them in `mobile-apps/` if you use them (they remain **gitignored**).

### What to use when

| Goal | Typical artifact | Notes |
|------|------------------|--------|
| **Physical iPhone / iPad** automation | Often **no file** | Install Wikipedia from the **App Store** (or **TestFlight** if you have access). Maestro flows can target the installed app by **bundle id** (`appId` in YAML). Appium uses `bundleId` and **does not** need an `.ipa` if the app is already installed. |
| **Simulator** (Maestro / Appium / Xcode) | **`Something.app`** from your build | Build the [Wikipedia iOS](https://github.com/wikimedia/wikipedia-ios) project in Xcode (or `xcodebuild`). Use the **`.app`** product under `DerivedData` / `Products` for the simulator. You can copy that bundle to `mobile-apps/` (e.g. `Wikipedia.app`) for a stable path in your own scripts—**simulator `.app` is not the same as a device `.ipa`**. |
| **Device install from a file** | **`wikipedia.ipa` (convention)** | If you have an Apple Developer account, **Archive** in Xcode → **Distribute App** → e.g. **Ad Hoc** or **Development** → you get an **`.ipa`**. Save it as **`mobile-apps/wikipedia.ipa`** (name is optional; keep it consistent with your Appium/Maestro config). That `.ipa` is signed **for your devices / provisioning profile**, not a global public binary. |

### Suggested on-disk names (all gitignored)

| Path | Use |
|------|-----|
| `mobile-apps/wikipedia.ipa` | Device-oriented archive **you** exported (Ad Hoc / Dev / Enterprise as applicable) |
| `mobile-apps/Wikipedia.app` | Simulator app bundle **you** copied from an Xcode build |

This repo’s **Maestro** and **Appium** examples are wired for **Android + `wikipedia.apk`**. To add iOS runs, point Maestro/Appium at `bundleId` and, where required, `app` / simulator `.app` paths per their docs—using the bundle id from your chosen build (Xcode **Signing & Capabilities** / target **Info** for the [Wikipedia iOS](https://github.com/wikimedia/wikipedia-ios) repo).
