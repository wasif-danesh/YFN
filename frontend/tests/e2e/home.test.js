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
  await expect(page.locator('path[data-sa2]')).toHaveCount(361)
  const search = page.getByRole('combobox')
  await search.fill('carl')
  await expect(page.getByRole('option').first()).toContainText('Carlton')
  await search.press('ArrowDown')
  await search.press('Enter')
  await expect(page.locator('.selected-area')).toContainText('Carlton')
  const polygon = page.locator('path[data-sa2="206041117"]')
  await polygon.click({ force: true })
  await expect(page.locator('.leaflet-popup-content')).toContainText('Carlton')
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
    .getByRole('link', { name: 'Compare this area' })
    .click()
  await expect(page).toHaveURL(/compare\?sa2=206041117/)
  await expect(page.locator('.comparison-table')).toContainText('$365')
  await page.getByRole('combobox').fill('footscray')
  await page
    .getByRole('option', { name: 'Footscray SA2 area', exact: true })
    .click()
  await expect(page.locator('.comparison-table')).toContainText('Footscray')
  await expect(page.locator('.comparison-table')).toContainText('2021 Census')
  await expect(page.locator('.comparison-table')).toContainText('Provisional')
  await page.reload()
  await expect(page.locator('.comparison-table')).toContainText('Carlton')
  await expect(page.locator('.comparison-table')).toContainText('Footscray')
  await page.screenshot({
    path: `test-results/compare-${test.info().project.name}.png`,
    fullPage: true,
  })
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
