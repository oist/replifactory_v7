import { createStore } from "vuex";
import experiment from "./experimentStore.js";

export default createStore({
  strict: process.env.NODE_ENV !== "production",
  state: {
    state_string: "Unknown",
    backendConnected: true,
    messages: [],
    debug: false,
  },
  modules: {
    experiment,
  },
  mutations: {
    initialiseStore() {
      if (localStorage.getItem("store")) {
        const store = JSON.parse(localStorage.getItem("store"));
        this.commit("setDebug", store.debug);
      }
    },
    setExperiments(state, experiments) {
      state.experiments = experiments;
    },
  },
  actions: {
    notifyInfo({ commit }, { title, content }) {
      commit("addMessage", {
        color: "info",
        title: title,
        content: content,
        autohide: true,
        delay: 5000,
      });
    },
    notifyWarning({ commit }, { title, content }) {
      commit("addMessage", {
        color: "warning",
        title: title != null ? title : "Warning",
        content: content,
        autohide: true,
        delay: 5000,
      });
    },
    notifySuccess({ commit }, { title, content }) {
      commit("addMessage", {
        color: "success",
        title: title,
        content: content,
        autohide: true,
        delay: 5000,
      });
    },
    notifyDanger({ commit }, { title, content }) {
      commit("addMessage", {
        color: "danger",
        title: title,
        content: content,
        autohide: true,
        delay: 5000,
      });
    },
    notify({ commit }, toast) {
      commit("addMessage", toast);
    },
  },
});
