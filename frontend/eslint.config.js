import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import jsxA11y from "eslint-plugin-jsx-a11y";
import tseslint from "typescript-eslint";

// CLAUDE.md §16/§18: lint is a required gate before any merge to develop/master.
export default tseslint.config(
  { ignores: ["dist", "coverage", "playwright-report", "test-results", "node_modules"] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended, jsxA11y.flatConfigs.recommended],
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2020,
      globals: { ...globals.browser, ...globals.node },
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],
      // Intentional pattern throughout this codebase (e.g. optional coupon
      // fields, IRD adapter records with sparse government data).
      "@typescript-eslint/no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
    },
  },
  {
    files: ["src/test/**/*.{ts,tsx}", "**/*.test.{ts,tsx}", "e2e/**/*.ts", "playwright.config.ts", "vite.config.ts", "vitest.config.ts"],
    languageOptions: {
      globals: { ...globals.node },
    },
    rules: {
      // Test/mock files legitimately use `any` for MSW request bodies and
      // loosely-typed fixture overrides.
      "@typescript-eslint/no-explicit-any": "off",
    },
  }
);
