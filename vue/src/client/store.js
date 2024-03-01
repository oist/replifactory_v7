import { createStore } from "vuex";
import device from "./deviceStore.js";
import experiment from "./experimentStore.js";
import machine from "./machineStore.js";
import security from "./securityStore.js";

import api from "@/api.js";
export default createStore({
  strict: process.env.NODE_ENV !== "production",
  state: {
    state_string: "Unknown",
    deviceConnected: false,
    deviceControlEnabled: true,
    experimentRunning: null,
    hostname: "replifactory_GUI",
    backendConnected: false,
    messages: [],
    debug: false,
  },
  modules: {
    device,
    experiment,
    machine,
    security,
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
    setDeviceConnected(state, value) {
      state.deviceConnected = value;
    },
    setHostname(state, hostname) {
      state.hostname = hostname;
    },
    setBackendConnected(state, connected) {
      state.backendConnected = connected;
    },
    addMessage(state, message) {
      state.messages.push(message);
    },
    setDebug(state, debug) {
      state.debug = debug;
    },
  },
  actions: {
    fetchHostname({ commit }) {
      api
        .get("/api/hostname")
        .then((response) => {
          commit("setHostname", response.data.hostname);
        })
        .catch((error) => {
          console.log(error);
        });
    },
    async connectDevice({ dispatch, commit }) {
      try {
        const response = await dispatch("/api/device/connect");
        if (response && response.data.success) {
          await dispatch("device/getAllDeviceData");
          commit("setDeviceConnected", true);
        } else {
          commit("setDeviceConnected", false);
        }
      } catch (error) {
        console.log(error);
        commit("setDeviceConnected", false);
      }
    },
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
