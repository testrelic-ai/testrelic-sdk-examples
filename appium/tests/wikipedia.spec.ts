import assert from 'node:assert';
import { $, browser } from '@wdio/globals';

async function dismissOptionalOnboarding(): Promise<void> {
  const labels = ['Skip', 'Get started', 'CONTINUE', 'Not now'];
  for (let round = 0; round < 6; round += 1) {
    let tapped = false;
    for (const text of labels) {
      const btn = $(`android=new UiSelector().text("${text}")`);
      if (await btn.isDisplayed().catch(() => false)) {
        await btn.click();
        tapped = true;
        await browser.pause(400);
      }
    }
    if (!tapped) {
      break;
    }
  }
}

describe('Wikipedia (Android)', () => {
  it('shows main UI after launch', async () => {
    await dismissOptionalOnboarding();

    const toolbarTitle = $('android=new UiSelector().textContains("Wikipedia")');
    const searchContainer = $('id=org.wikipedia:id/search_container');

    await toolbarTitle.waitForDisplayed({ timeout: 45_000 }).catch(async () => {
      await searchContainer.waitForDisplayed({ timeout: 45_000 });
    });

    const toolbarOk = await toolbarTitle.isDisplayed().catch(() => false);
    const searchOk = await searchContainer.isDisplayed().catch(() => false);
    assert.ok(toolbarOk || searchOk, 'Expected Wikipedia toolbar title or search container');
  });
});
