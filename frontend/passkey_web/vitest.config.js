import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./setupTests.js'],
    include: ['src/**/*.test.{js,ts}', 'tests/**/*.test.{js,ts}'],
    globals: true,
  },
});
