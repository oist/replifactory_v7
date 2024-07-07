import { resolve } from "path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
// import alias from "@rollup/plugin-alias";

// https://vitejs.dev/config/
export default defineConfig({
  // mode: 'production',
  // resolve: {
  //   alias: {
  //     vue: "vue/dist/vue.esm-bundler.js",
  //   },
  // },
  plugins: [
    vue({isProduction: true,}),
    // alias(),
    // alias({
    //   entries: [
    //     // { find: "vue", replacement: "vue/dist/vue.esm-bundler.js" },
    //     { find: 'vue', replacement: resolve(__dirname,'node_modules/vue/dist/vue.esm-bundler.js') }
    //   ],
    // }),
  ],
  build: {
    outDir: resolve(__dirname, "../static"),
    minify: false,
    lib: {
      formats: ["umd"],
      // entry: {
      //   "endless-growth-experiment-description": "src/components/ExperimentDescription.vue",
      //   "endless-growth-experiment-parameters": "src/components/ExperimentParameters.vue",
      // },
      // entry: ["src/components/ExperimentDescription.vue", "src/components/ExperimentParameters.vue"],
      // name: ["endless-growth-experiment-description", "endless-growth-experiment-parameters"],
      // fileName: ["endless-growth-experiment-description", "endless-growth-experiment-parameters"],
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
  // resolve: {
  //   alias: {
  //     // 'vue': resolve(__dirname, 'node_modules/vue/dist/vue.esm-bundler.js'),
  //     // 'vue': resolve(__dirname, 'node_modules/vue/dist/vue.esm-bundler.js'),
  //     // 'vue$': 'vue/dist/vue.esm-bundler.js',
  //     vue: 'vue/dist/vue.runtime.esm-bundler.js',
  //     Vue: 'vue/dist/vue.runtime.esm-bundler.js',
  //   }
  // },
});
