import { resolve } from "path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  resolve: {
		alias: {
			'vue': 'vue/dist/vue.esm-bundler.js',
		},
	},
  plugins: [vue()],
  build: {
    outDir: resolve(__dirname, "../static"),
    lib: {
      formats: ['es', 'umd'],
      // Could also be a dictionary or array of multiple entry points
      // entry: resolve(__dirname, "src/plugin.js"),
      entry: resolve(__dirname, "src/components/ExperimentParameters.vue"),
      name: "ReplifactoryPlugin",
      // the proper extensions will be added
      // fileName: "replifactory-plugin",
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
