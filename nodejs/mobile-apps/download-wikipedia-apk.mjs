#!/usr/bin/env node
/**
 * Downloads the production Wikipedia Android APK (application id `org.wikipedia`)
 * from F-Droid into this directory as `wikipedia.apk`.
 *
 * Source: https://f-droid.org/en/packages/org.wikipedia/
 */

import fs from 'node:fs';
import path from 'node:path';
import { pipeline } from 'node:stream/promises';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outPath = path.join(__dirname, 'wikipedia.apk');

const FDROID_META = 'https://f-droid.org/api/v1/packages/org.wikipedia';

async function main() {
  const metaRes = await fetch(FDROID_META);
  if (!metaRes.ok) {
    throw new Error(`F-Droid metadata failed: ${metaRes.status} ${metaRes.statusText}`);
  }
  /** @type {{ suggestedVersionCode?: number }} */
  const meta = await metaRes.json();
  const code = meta.suggestedVersionCode;
  if (typeof code !== 'number') {
    throw new Error('F-Droid API response missing suggestedVersionCode');
  }

  const apkUrl = `https://f-droid.org/repo/org.wikipedia_${code}.apk`;
  process.stderr.write(`Downloading Wikipedia APK (versionCode ${code})…\n${apkUrl}\n`);

  const apkRes = await fetch(apkUrl);
  if (!apkRes.ok) {
    throw new Error(`APK download failed: ${apkRes.status} ${apkRes.statusText}`);
  }
  if (!apkRes.body) {
    throw new Error('APK response has no body');
  }

  await fs.promises.rm(outPath, { force: true });
  const tmp = `${outPath}.part`;
  await fs.promises.rm(tmp, { force: true });
  const fileStream = fs.createWriteStream(tmp);
  await pipeline(apkRes.body, fileStream);
  await fs.promises.rename(tmp, outPath);

  const st = await fs.promises.stat(outPath);
  process.stderr.write(`Wrote ${outPath} (${(st.size / 1024 / 1024).toFixed(1)} MiB)\n`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
