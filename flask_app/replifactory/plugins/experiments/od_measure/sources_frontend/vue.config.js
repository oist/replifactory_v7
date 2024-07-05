const path = require("path");

const vueSrc = "./src";

module.exports = {
    configureWebpack: {
      resolve: {
        alias: {
          '@': path.join(__dirname, vueSrc),
          'vue$': 'vue/dist/vue.esm-bundler.js',
        }
      },
    },
    css: {
      extract: false,
    },
    outputDir: path.resolve(__dirname, "../static"),
    productionSourceMap: false,
  }
