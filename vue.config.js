const path = require("path");
const publicDir = "vue/public";

module.exports = {
  outputDir: path.join(__dirname, "flask_app", "static", "build"),
  publicPath: "/static/build/",
  configureWebpack: {
    context: path.join(__dirname, "vue"),
    resolve: {
      alias: {
        "@": path.join(__dirname, "vue", "src"),
      },
      fallback: {
        stream: require.resolve("stream-browserify"),
        assert: require.resolve("assert/"),
      },
    },
    // entry: {
    //   main: "./src/main.js",
    // },
    output: {
      chunkFilename: "[id].js",
      filename: "[name].bundle.js",
    },
    devtool: "source-map",
  },
  productionSourceMap: true,
  chainWebpack: (config) => {
    config.resolve.alias.set("vue", "@vue/compat");
    config.module
      .rule("vue")
      .use("vue-loader")
      .tap((options) => {
        return {
          ...options,
          compilerOptions: {
            compatConfig: {
              MODE: 2,
            },
          },
        };
      });
    // change the template path for the html plugin
    config.plugin("html").tap((args) => {
      args[0].template = path.resolve(publicDir + "/index.html");
      return args;
    });
    // change the from path for the copy plugin
    // config.plugin("copy").tap(([pathConfigs]) => {
    //   pathConfigs[0].from = path.resolve(publicDir);
    //   return [pathConfigs];
    // });
  },
  devServer: {
    // publicPath: "/",
    proxy: {
      "/api": {
        ws: true,
        changeOrigin: true,
        target: "http://localhost:5000",
      },
      "/socket.io": {
        ws: true,
        changeOrigin: true,
        target: "http://localhost:5000",
      },
    },
  },
};
