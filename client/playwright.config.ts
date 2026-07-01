import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './src',
  testMatch: '**/*.e2e.spec.ts',
  use: {
    baseURL: process.env.CI
      ? 'http://localhost:4173'   // CI: vite preview
      : 'http://localhost:5173',  // 本地: vite dev
    headless: true,
  },
  webServer: process.env.CI
    ? {
        command: 'npx vite preview --port 4173',
        port: 4173,
        reuseExistingServer: true,
      }
    : {
        command: 'npm run dev',
        port: 5173,
        reuseExistingServer: true,
      },
})