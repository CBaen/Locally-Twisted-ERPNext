import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";

const rootDir = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        playcanvas: resolve(rootDir, "playcanvas.html"),
        babylon: resolve(rootDir, "babylon.html"),
        classicPlaycanvas: resolve(rootDir, "classic-playcanvas.html"),
        classicPlaycanvasV2: resolve(rootDir, "classic-playcanvas-v2.html")
      }
    }
  }
});
