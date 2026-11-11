import { defineConfig } from '@playwright/test';

// The tests need the API (port 8080) and the Angular dev server (port 4200).
// Both are started automatically unless they are already running.
export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:4200',
    trace: 'on-first-retry',
  },
  webServer: [
    {
      command: 'mvn -q -f ../api/pom.xml spring-boot:run',
      url: 'http://localhost:8080/api/runs',
      reuseExistingServer: true,
      timeout: 180_000,
    },
    {
      command: 'npx ng serve --port 4200',
      url: 'http://localhost:4200',
      reuseExistingServer: true,
      timeout: 180_000,
    },
  ],
});
