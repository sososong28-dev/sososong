const { test, expect } = require('@playwright/test');

test('dashboard and navigation', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Dashboard/);
  const cards = page.locator('[data-testid="node-card"]');
  await expect(cards).toHaveCount(3);
  await expect(cards.first()).toContainText('状态');
  await cards.first().click();
  await expect(page.locator('#title')).toBeVisible();
  await page.click('#checkBtn');
  await expect(page.locator('#machine')).toContainText('status');
  await page.goto('/');
  await page.click('#refreshBtn');
  await page.goto('/tasks');
  await expect(page.locator('h2')).toContainText('最近任务执行记录');
});
