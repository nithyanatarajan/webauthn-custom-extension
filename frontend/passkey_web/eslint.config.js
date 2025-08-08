import {defineConfig, globalIgnores} from 'eslint/config';
import globals from 'globals';
import js from '@eslint/js';
import eslintConfigPrettier from 'eslint-config-prettier/flat';

export default defineConfig([
  {
    name: 'global-env',
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.es2021,
      },
    },
    linterOptions: {
      reportUnusedDisableDirectives: true,
    },
  },
  {
    name: 'javascript-rules',
    files: ['**/*.{js,cjs,mjs,jsx,vue}'],
    ...js.configs.recommended,
  },

  // Vitest globals for test files only
  {
    name: 'vitest-tests',
    files: ['**/*.{test,spec}.?(c|m)js'],
    languageOptions: {
      globals: {
        ...globals.node, // allow import.meta, process in tests if needed
        // Vitest globals
        describe: 'readonly',
        it: 'readonly',
        test: 'readonly',
        expect: 'readonly',
        vi: 'readonly',
        beforeAll: 'readonly',
        afterAll: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
      },
    },
  },

  globalIgnores(['**/dist/**', '**/dist-ssr/**', '**/coverage/**']),

  // Prettier compatibility (disable ESLint formatting rules)
  eslintConfigPrettier,
]);
