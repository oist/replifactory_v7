import { createApp } from "vue";
import CoreuiVue from "@coreui/vue";
import BootstrapVueNext from "bootstrap-vue-next";
import * as icons from "@coreui/icons";

import App from "./client/App.vue";
import store from "./client/store";
import router from "./client/router";

// Import Bootstrap and CoreUI styles
import "@coreui/coreui/dist/css/coreui.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue-next/dist/bootstrap-vue-next.css";

// Important for loading plugins
// will be replaced by vite.config.js to use vue.esm-bundler.js
import * as Vue from 'vue';
window.Vue = Vue;

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
app.mount("#replifactory");
