import { resolve } from "node:path";
import { defineConfig } from "vite";

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        playcanvas: resolve(__dirname, "playcanvas.html"),
        babylon: resolve(__dirname, "babylon.html")
      }
    }
  }
});
