const { test, expect } = require('@playwright/test');

test('dashboard and navigation', async ({ page }) => {
  await page.addInitScript(() => window.localStorage.setItem('apiToken', 'change-me'));
  await page.goto('/');
  await expect(page).toHaveTitle(/Dashboard/);
  await expect(page.locator('#summaryCards')).toBeVisible();
  await page.click('#checkAllBtn');
  const cards = page.locator('[data-testid="node-card"]');
  await expect(cards).toHaveCount(3);
  await expect(cards.nth(1)).toContainText(/win-openclaw-01|win-openclaw-02/);
  await expect(cards.first()).toContainText('最近 Token');
  await cards.first().click();
  await expect(page.locator('#title')).toBeVisible();
  await expect(page.locator('#tokenRows')).toBeVisible();
  await page.click('#checkBtn');
  await expect(page.locator('#machine')).toContainText('last_token_total');
  await page.goto('/tasks');
  await expect(page.locator('#usageRows')).toBeVisible();
});
