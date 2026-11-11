import { expect, test } from '@playwright/test';

test.describe('Intent review dashboard', () => {
  test('shows each run with its recorded accuracy', async ({ page }) => {
    await page.goto('/');
    const cards = page.locator('mat-card.run-card');
    await expect(cards).toHaveCount(4);
    await expect(cards.filter({ hasText: 'Model A' })).toContainText('75%');
    await expect(cards.filter({ hasText: 'Model B' })).toContainText('94%');
    await expect(cards.filter({ hasText: 'Claude Haiku 5.5 with rubric prompt: gold set' })).toContainText('100%');
  });

  test('errors-only shows the nine misses for Model A', async ({ page }) => {
    await page.goto('/');
    await page.locator('mat-card.run-card', { hasText: 'Model A' }).getByRole('button', { name: 'View' }).click();
    await page.getByRole('switch', { name: 'Errors only' }).check();
    const rows = page.locator('table tr[mat-row]');
    await expect(rows).toHaveCount(9);
    await expect(page.locator('td span.miss')).toHaveCount(9);
  });

  test('language filter narrows the rows', async ({ page }) => {
    await page.goto('/');
    await page.locator('mat-card.run-card', { hasText: 'Model A' }).getByRole('button', { name: 'View' }).click();
    await page.getByLabel('Language').click();
    await page.getByRole('option', { name: 'Spanish' }).click();
    await expect(page.locator('table tr[mat-row]')).toHaveCount(12);
  });

  test('page fits a phone-width screen without horizontal scrolling', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 800 });
    await page.goto('/');
    await expect(page.locator('mat-card.run-card').first()).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(0);
  });
});
