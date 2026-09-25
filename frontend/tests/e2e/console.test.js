import { test, expect } from '@playwright/test'

test('API test console calls the real API, shows JSON, handles errors and reloads', async ({ page }) => {
  const browserErrors = []
  page.on('pageerror', error => browserErrors.push(error.message))
  // The browser must work even when an extension blocks the hosting health URL.
  await page.route('**/health', route => route.abort('blockedbyclient'))
  await page.goto('/api-test-console')
  await expect(page.getByText('4 of 4 requests successful')).toBeVisible()
  await expect(page.getByTestId('health').locator('pre')).toContainText('"database": "ready"')
  await expect(page.getByTestId('details').locator('pre')).toContainText('25267')
  await expect(page.getByTestId('details').locator('pre')).toContainText('"publication_ready": true')
  await page.getByLabel('Comparison SA2 codes').fill('206041117')
  await page.getByRole('button', { name: 'Run Compare areas', exact: true }).click()
  await expect(page.getByTestId('compare')).toContainText('HTTP 422')
  await expect(page.getByTestId('compare').locator('pre')).toContainText('INVALID_SELECTION')
  await page.getByLabel('Comparison SA2 codes').fill('206041117,213031348')
  await page.getByRole('button', { name: 'Run Compare areas', exact: true }).click()
  await expect(page.getByText('4 of 4 requests successful')).toBeVisible()
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
  await page.screenshot({ path: `test-results/console-${test.info().project.name}.png`, fullPage: true })
  await page.reload()
  await expect(page.getByText('4 of 4 requests successful')).toBeVisible()
  expect(browserErrors).toEqual([])
})
