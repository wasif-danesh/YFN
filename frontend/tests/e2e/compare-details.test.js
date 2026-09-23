import { test, expect } from '@playwright/test'
const selection = '206041117,213031348'

test('complete comparison links to population history and restores selection after reload', async ({
  page,
}) => {
  const errors = []
  page.on('pageerror', (error) => errors.push(error.message))
  await page.goto(`/compare?sa2=${selection}`)
  await expect(
    page.getByRole('heading', { name: 'Compare Melbourne areas' }),
  ).toBeVisible()
  await expect(
    page.getByRole('columnheader', { name: 'What it means' }),
  ).toBeVisible()
  await expect(page.locator('.rent-insight')).toContainText('$10 higher')
  const rent = page.locator(
    '[data-measure="rent_weekly"] [data-area="206041117"]',
  )
  await rent.getByText('Source & coverage notes').click()
  await expect(rent).toContainText('Australian Bureau of Statistics')
  await rent.getByText('Source & coverage notes').click()
  await page.screenshot({
    path: `test-results/compare-complete-${test.info().project.name}.png`,
    fullPage: true,
  })
  await page.getByRole('link', { name: 'View Carlton details' }).click()
  await expect(
    page.getByRole('heading', { name: 'Carlton', exact: true }),
  ).toBeVisible()
  await expect(
    page.getByRole('link', { name: 'API test console' }),
  ).toHaveCount(0)
  await expect(page.locator('.population-table')).toContainText('25,267')
  await expect(page.locator('.population-summary')).toContainText('4,402')
  await expect(page.locator('.population-table')).toContainText('preliminary')
  await expect(page.locator('.population-chart circle')).toHaveCount(6)
  await page.reload()
  await expect(
    page.getByRole('heading', { name: 'Carlton', exact: true }),
  ).toBeVisible()
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true)
  await page.screenshot({
    path: `test-results/area-details-${test.info().project.name}.png`,
    fullPage: true,
  })
  await page
    .getByRole('link', { name: 'Back to comparison', exact: true })
    .last()
    .click()
  await expect(page.locator('.comparison-table')).toContainText('Footscray')
  expect(new URL(page.url()).searchParams.get('sa2')).toBe(selection)
  // With 2+ areas already selected, the search/map panel starts collapsed
  // to a compact chip bar so the comparison sits above the fold.
  await page.getByRole('button', { name: 'Edit areas' }).click()
  await page.getByRole('button', { name: 'Add a third area' }).click()
  await expect(page.getByRole('combobox')).toBeFocused()
  await page.getByRole('combobox').fill('clayton')
  await page.getByRole('option').first().click()
  await expect(
    page.getByText('3 of 3 areas selected', { exact: true }),
  ).toBeVisible()
  await expect(page.locator('#selection-title')).toBeFocused()
  await page
    .getByRole('button', { name: 'Remove Carlton', exact: true })
    .click()
  await expect(page.getByRole('combobox')).toBeFocused()
  expect(errors).toEqual([])
})

test('API failures, unavailable measures and unknown area links are recoverable', async ({
  page,
}) => {
  await page.route('**/api/v1/compare?*', (route) =>
    route.fulfill({
      status: 503,
      contentType: 'application/json',
      body: JSON.stringify({
        error: { message: 'Area data is temporarily unavailable.' },
      }),
    }),
  )
  await page.goto(`/compare?sa2=${selection}`)
  await expect(page.getByRole('alert')).toContainText('temporarily unavailable')
  await page.unroute('**/api/v1/compare?*')
  await page.getByRole('button', { name: 'Try again', exact: true }).click()
  await expect(page.locator('.comparison-table')).toContainText('$365')
  await page.route('**/api/v1/compare?*', async (route) => {
    const response = await route.fetch()
    const body = await response.json()
    // Explicit test-only missing value, never written to the maintained database.
    body.areas[0].indicators[0].raw_value = null
    body.areas[0].indicators[0].quality = {
      status: 'unavailable',
      reason: 'Test-only suppressed value',
      coverage_fraction: null,
    }
    await route.fulfill({ response, json: body })
  })
  await page.reload()
  await expect(
    page.locator('[data-measure="rent_weekly"] [data-area="206041117"]'),
  ).toContainText('Not available')
  await expect(page.locator('.rent-insight')).toContainText('not shown')
  await page.goto('/areas/999999999?compare=bad')
  await expect(page.getByRole('alert')).toContainText('not found')
  await expect(
    page.getByRole('link', { name: 'Choose another area' }),
  ).toHaveAttribute('href', '/')
})
