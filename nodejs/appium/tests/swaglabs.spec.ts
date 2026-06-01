import assert from 'node:assert';
import { $, browser } from '@wdio/globals';

const USERNAME_FIELD = '~test-Username';
const PASSWORD_FIELD = '~test-Password';
const LOGIN_BUTTON = '~test-LOGIN';
const PRODUCTS_HEADER = '~test-Cart drop zone';

async function resetToLogin(): Promise<void> {
  await browser.execute('mobile: clearApp', { appId: 'com.swaglabsmobileapp' });
  await browser.execute('mobile: activateApp', { appId: 'com.swaglabsmobileapp' });
  await $(USERNAME_FIELD).waitForDisplayed({ timeout: 30_000 });
}

describe('Swag Labs (Android)', () => {
  beforeEach(async () => {
    await resetToLogin();
  });

  it('shows the login screen after launch', async () => {
    const username = $(USERNAME_FIELD);
    const password = $(PASSWORD_FIELD);
    const login = $(LOGIN_BUTTON);

    await username.waitForDisplayed({ timeout: 30_000 });
    assert.ok(await password.isDisplayed(), 'Password field should be visible');
    assert.ok(await login.isDisplayed(), 'LOGIN button should be visible');
  });

  it('logs in with standard_user and lands on the products screen', async () => {
    await $(USERNAME_FIELD).setValue('standard_user');
    await $(PASSWORD_FIELD).setValue('secret_sauce');
    await $(LOGIN_BUTTON).click();

    const productsHeader = $(PRODUCTS_HEADER);
    await productsHeader.waitForDisplayed({ timeout: 30_000 });
    assert.ok(await productsHeader.isDisplayed(), 'Products screen drop zone should be visible after login');
  });

  it('rejects invalid credentials', async () => {
    await $(USERNAME_FIELD).setValue('locked_out_user');
    await $(PASSWORD_FIELD).setValue('secret_sauce');
    await $(LOGIN_BUTTON).click();

    const errorBanner = $('android=new UiSelector().textContains("locked out")');
    await errorBanner.waitForDisplayed({ timeout: 15_000 });
    assert.ok(await errorBanner.isDisplayed(), 'Locked-out error banner should be visible');
  });
});
