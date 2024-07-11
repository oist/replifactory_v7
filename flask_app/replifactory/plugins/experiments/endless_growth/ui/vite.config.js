import { resolve } from "path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [
    vue({isProduction: true,}),
  ],
  build: {
    outDir: resolve(__dirname, "../static"),
    minify: false,
    lib: {
      formats: ["umd"],
    },
    rollupOptions: {
      // make sure to externalize deps that shouldn't be bundled
      // into your library
      external: ["vue"],
      output: {
        // Provide global variables to use in the UMD build
        // for externalized deps
        globals: {
          vue: "Vue",
        },
        format: "umd",
      },
    },
  },
});
