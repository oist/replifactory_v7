// import Vue from 'vue';
import { createStore } from "vuex";
// import Vuex from 'vuex';
import device from "./deviceStore.js";
import experiment from "./experimentStore.js";
// Vue.use(Vuex);

import api from "@/api.js";
export default createStore({
  state: {
    state_string: "Unknown",
    deviceConnected: false,
    deviceControlEnabled: true,
    experimentRunning: null,
    hostname: "replifactory_GUI",
  },
  modules: {
    device,
    experiment,
  },
  mutations: {
    setExperiments(state, experiments) {
      state.experiments = experiments;
    },
    setDeviceConnected(state, value) {
      state.deviceConnected = value;
    },
    setHostname(state, hostname) {
      state.hostname = hostname;
    },
  },
  actions: {
    fetchHostname({ commit }) {
      api
        .get("/hostname")
        .then((response) => {
          commit("setHostname", response.data.hostname);
        })
        .catch((error) => {
          console.log(error);
        });
    },
    async connectDevice({ dispatch, commit }) {
      try {
        const response = await dispatch("device/connect");
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
  },
});
