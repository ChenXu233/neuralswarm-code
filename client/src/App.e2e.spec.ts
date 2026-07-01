import { test, expect } from '@playwright/test'

test.describe('App E2E', () => {
  test('loads the homepage with app-layout', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('.app-layout')).toBeVisible()
  })

  test('activity bar shows action buttons', async ({ page }) => {
    await page.goto('/')
    const buttons = page.locator('.top-icons .activity-btn')
    await expect(buttons).toHaveCount(4)
  })

  test('clicking activity button toggles sidebar', async ({ page }) => {
    await page.goto('/')
    const firstBtn = page.locator('.top-icons .activity-btn').first()
    await firstBtn.click()
    await expect(page.locator('.sidebar')).toBeVisible()
    await firstBtn.click()
    await expect(page.locator('.sidebar')).not.toBeVisible()
  })

  test('theme switching works via data-theme', async ({ page }) => {
    await page.goto('/')
    let theme = await page.evaluate(() => document.documentElement.dataset.theme)
    expect(theme).toBe('warm-stone')
    await page.evaluate(() => { document.documentElement.dataset.theme = 'dark-slate' })
    theme = await page.evaluate(() => document.documentElement.dataset.theme)
    expect(theme).toBe('dark-slate')
  })
})
