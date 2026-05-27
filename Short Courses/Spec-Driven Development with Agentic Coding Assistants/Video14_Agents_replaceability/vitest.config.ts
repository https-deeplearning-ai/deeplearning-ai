import { defineConfig } from "vitest/config";

export default defineConfig({
  oxc: {
    transform: {
      jsxImportSource: "hono/jsx",
    },
  },
});
