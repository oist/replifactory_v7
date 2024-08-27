// Important for loading plugins
// will be replaced by vite.config.js to use vue.esm-bundler.js
import * as Vue from "vue";
window.Vue = Vue;

(async () => {
  const { createApp } = Vue;
  const CoreuiVue = await import("@coreui/vue").then((m) => m.default);
  const BootstrapVueNext = await import("bootstrap-vue-next").then(
    (m) => m.default,
  );
  const icons = await import("@coreui/icons");
  const __version__ = await import("@/versions.js").then((m) => m.default);

  const App = await import("./client/App.vue").then((m) => m.default);
  const store = await import("./client/store").then((m) => m.default);
  const router = await import("./client/router").then((m) => m.default);

  await import("@coreui/coreui/dist/css/coreui.css");
  await import("bootstrap/dist/css/bootstrap.css");
  await import("bootstrap-vue-next/dist/bootstrap-vue-next.css");
  await import("bootstrap-icons/font/bootstrap-icons.min.css");
  await import("bootstrap/dist/js/bootstrap.bundle.min.js");

  const app = createApp(App);

  app.directive("click-outside", {
    beforeMount(el, binding) {
      el.clickOutsideEvent = (event) => {
        // check that click was outside the el and his children, and not an element with class "input"
        if (
          !(el === event.target || el.contains(event.target)) &&
          !event.target.classList.contains("input")
        ) {
          // if it did, call method provided in attribute value
          binding.value();
        }
      };
      document.addEventListener("click", el.clickOutsideEvent);
    },
    beforeUnmount(el) {
      document.removeEventListener("click", el.clickOutsideEvent);
    },
  });

  app.use(CoreuiVue);
  app.use(BootstrapVueNext);
  app.use(store);
  app.use(router);
  app.provide("icons", icons);
  app.provide("appVersion", __version__);
  app.mount("#replifactory");
})();
