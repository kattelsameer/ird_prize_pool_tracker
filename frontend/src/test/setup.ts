import "@testing-library/jest-dom/vitest";
import { afterAll, afterEach, beforeAll } from "vitest";
import { server } from "./server";
import { resetMockData } from "./handlers";

// Ensure component tests never depend on a live network (§54): every request in tests goes
// through MSW; anything unhandled fails loudly instead of silently hitting the real network.
beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  server.resetHandlers();
  resetMockData();
  window.localStorage.clear();
});
afterAll(() => server.close());

// jsdom doesn't implement matchMedia; several components/theme queries rely on it.
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

// This project's jsdom/Vitest combo doesn't provide window.localStorage either (confirmed:
// it's `undefined`, not just unimplemented methods) -- api/client.ts's token storage needs it.
// A minimal in-memory Storage polyfill, reset between tests as part of afterEach below.
if (!window.localStorage) {
  const store = new Map<string, string>();
  const localStoragePolyfill: Storage = {
    getItem: (key) => (store.has(key) ? store.get(key)! : null),
    setItem: (key, value) => {
      store.set(key, String(value));
    },
    removeItem: (key) => {
      store.delete(key);
    },
    clear: () => {
      store.clear();
    },
    key: (index) => Array.from(store.keys())[index] ?? null,
    get length() {
      return store.size;
    },
  };
  Object.defineProperty(window, "localStorage", { writable: true, value: localStoragePolyfill });
}
