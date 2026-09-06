import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "node:path";

export default defineConfig({
  plugins: [react()],
  base: "/mmip_crisis/",
  build: {
    rollupOptions: {
      input: {
        index: resolve(__dirname, "index.html"),
        map: resolve(__dirname, "continental-us-map.html"),
        jurisdictionHistory: resolve(__dirname, "jurisdiction-history-sample.html"),
      },
    },
  },
});
