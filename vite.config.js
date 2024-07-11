// vite.config.js
import { resolve } from "path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { nodePolyfills } from "vite-plugin-node-polyfills";

/** @type {import('vite').UserConfig} */
export default defineConfig({
  // https://vitejs.dev/config/
  plugins: [vue(), nodePolyfills()],
  define: {
    "process.env": {},
  },
  resolve: {
    alias: {
      "@": resolve(__dirname, "vue/src"),
      vue: "vue/dist/vue.esm-bundler.js",
    },
  },
  root: "./vue",
  base: "/",
  publicDir: "./public",
  build: {
    outDir: resolve(__dirname, "flask_app/static/build"),
    assetsDir: "./",
    rollupOptions: {
      input: resolve(__dirname, "vue/index.html"),
    },
    sourcemap: true,
  },
  css: {
    devSourcemap: true,
  },
  server: {
    port: 8080,
    open: true,
    proxy: {
      "/plugins": {
        changeOrigin: false,
        target: "http://localhost:5000",
      },
      "/static": {
        changeOrigin: false,
        target: "http://localhost:5000",
      },
      "/security": {
        changeOrigin: false,
        target: "http://localhost:5000",
      },
      "/api/": {
        changeOrigin: true,
        target: "http://localhost:5000",
        secure: false,
      },
      "/socket.io": {
        ws: true,
        target: "http://localhost:5000",
      },
    },
  },
});
