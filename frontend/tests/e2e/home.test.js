import { test, expect } from '@playwright/test'

// Core journey tests do not depend on a third-party tile server.
test.beforeEach(async ({ page }) => {
  await page.route('https://tile.openstreetmap.org/**', (route) =>
    route.abort(),
  )
})

test('home search, map selection, comparison and reload work with real data', async ({
  page,
}) => {
  const errors = []
  page.on('pageerror', (error) => errors.push(error.message))
  await page.goto('/')
  await expect(
    page.getByRole('heading', { name: 'Find your place in Melbourne.' }),
  ).toBeVisible()
  await expect(
    page.getByRole('link', { name: 'API test console' }),
  ).toHaveCount(0)
  await expect(page.locator('path[data-sa2]')).toHaveCount(361)
  const search = page.getByRole('combobox')
  await search.fill('carl')
  await expect(page.getByRole('option').first()).toContainText('Carlton')
  await search.press('ArrowDown')
  await search.press('Enter')
  await expect(page.locator('.selected-area')).toContainText('Carlton')
  await expect(
    page.getByRole('link', { name: 'Compare 2 areas' }),
  ).toHaveCount(0)
  const polygon = page.locator('path[data-sa2="213031348"]')
  await polygon.dispatchEvent('click')
  await expect(page.locator('.selected-area')).toContainText('Footscray')
  await expect(page.locator('.selected-area')).toContainText('2 of 3 selected')
  await page.getByRole('combobox').fill('clayton')
  await page
    .getByRole('option', { name: 'Clayton - Central SA2 area', exact: true })
    .click()
  await expect(page.locator('.selected-area')).toContainText('3 of 3 selected')
  await expect(page.getByRole('combobox')).toHaveCount(0)
  await page
    .getByRole('button', { name: 'Remove Clayton - Central' })
    .click()
  await expect(page.locator('.selected-area')).toContainText('2 of 3 selected')
  await expect(page.getByRole('combobox')).toBeVisible()
  await expect(page.locator('.tile-notice')).toBeVisible()
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true)
  await page.screenshot({
    path: `test-results/home-${test.info().project.name}.png`,
    fullPage: true,
  })
  await page
    .locator('.selected-area')
    .getByRole('link', { name: 'Compare 2 areas' })
    .click()
  await expect(page).toHaveURL(/\/compare\?sa2=/)
  expect(new URL(page.url()).searchParams.get('sa2')).toBe(
    '206041117,213031348',
  )
  await expect(page.locator('.comparison-table')).toContainText('$365')
  await expect(
    page.getByRole('link', { name: 'API test console' }),
  ).toHaveCount(0)
  await expect(page.locator('.comparison-table')).toContainText('Footscray')
  await expect(page.locator('.comparison-table')).toContainText('2021 Census')
  await expect(page.locator('.comparison-table')).toContainText(
    'Source & coverage notes',
  )
  await page.reload()
  await expect(page.locator('.comparison-table')).toContainText('Carlton')
  await expect(page.locator('.comparison-table')).toContainText('Footscray')
  await page.screenshot({
    path: `test-results/compare-${test.info().project.name}.png`,
    fullPage: true,
  })
  // With 2+ areas already selected, the search/map panel starts collapsed
  // to a compact chip bar so the comparison sits above the fold.
  await page.getByRole('button', { name: 'Edit areas' }).click()
  await page.getByRole('combobox').fill('clayton')
  await page.getByRole('option').first().click()
  await expect(
    page.getByText('Three areas selected. Remove one to choose another.'),
  ).toBeVisible()
  await expect(page.getByRole('combobox')).toHaveCount(0)
  await page
    .getByRole('button', { name: 'Remove Carlton', exact: true })
    .click()
  await expect(page.getByRole('combobox')).toBeVisible()
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true)
  expect(errors).toEqual([])
})

test('invalid comparison selection and failed map remain recoverable', async ({
  page,
}) => {
  await page.goto('/compare?sa2=bad')
  await expect(page.getByRole('alert')).toContainText('Choose up to three')
  await page.getByRole('link', { name: 'Clear selection' }).click()
  await expect(
    page.getByText('A fresh start, one area at a time.'),
  ).toBeVisible()
  await page.route('**/maps/greater-melbourne-sa2.geojson', (route) =>
    route.abort(),
  )
  await page.goto('/')
  await expect(page.getByRole('alert')).toContainText('map couldn’t load')
  await page.getByRole('combobox').fill('carl')
  await expect(page.getByRole('option').first()).toContainText('Carlton')
})
