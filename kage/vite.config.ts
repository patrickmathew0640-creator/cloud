import { fileURLToPath } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const local = (path: string) => fileURLToPath(new URL(path, import.meta.url));

// The configured usage imports from the ThreeUI package; resolve it to the
// registered sources vendored in src/shaders so the build uses exactly those.
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [
      { find: "@designcodeio/threeui/style.css", replacement: local("./src/shaders/threeui.css") },
      { find: /^@designcodeio\/threeui$/, replacement: local("./src/threeui.ts") },
    ],
  },
});
