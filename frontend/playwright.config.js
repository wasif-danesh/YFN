import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  workers: 1,
  use: { baseURL: 'http://127.0.0.1:4173', trace: 'retain-on-failure' },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['Pixel 7'] } },
  ],
  webServer: [
    { command: 'node scripts/serve-static.mjs', url: 'http://127.0.0.1:4173', reuseExistingServer: false },
    { command: 'python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000', cwd: '..',
      url: 'http://127.0.0.1:8000/health', reuseExistingServer: false,
      env: { CORS_ALLOWED_ORIGINS: '["http://127.0.0.1:4173"]' } },
  ],
})
