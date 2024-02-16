module.exports = {
  root: true,
  env: {
    node: true,
    es2022: true,
    "vue/setup-compiler-macros": true,
  },
  extends: ["eslint:recommended", "plugin:vue/vue3-recommended", "prettier"],
  rules: {
    "no-console": process.env.NODE_ENV === "production" ? "warn" : "off",
    "no-debugger": process.env.NODE_ENV === "production" ? "warn" : "off",
  },
  overrides: [
    {
      files: ["vue/src/**/*.vue"],
      rules: {
        "vue/no-multiple-template-root": "off",
      },
    },
  ],
};
