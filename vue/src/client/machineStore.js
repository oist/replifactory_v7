import api from "@/api.js";

const DISCONNECTED_STATES = [
  "OFFLINE",
  "NONE",
  "CLOSED",
  "CLOSED_WITH_ERROR",
  "UNKNOWN",
];
const MANUAL_CONTROL_STATES = ["OPERATIONAL", "PAUSED"];

export default {
  namespaced: true,
  state: {
    connection: {
      current: {
        id: null,
      },
      options: {
        devices: {},
      },
    },
    machineState: {
      id: "UNKNOWN",
      string: "Unknown",
    },
    devices: {},
  },
  mutations: {
    updateConnectionOptions(state, options) {
      state.connection.options = options;
    },
    updateCurrentConnetion(state, connection) {
      state.connection.current = connection;
    },
    updateMachineState(state, machineState) {
      state.machineState = machineState;
    },
    updateDevices(state, devices) {
      const new_value = { ...state.devices, ...devices };
      state.devices = new_value;
    },
  },
  getters: {
    isDisconnected(state) {
      return DISCONNECTED_STATES.includes(state.machineState.id);
    },
    isConnected(state, getters) {
      return !getters.isDisconnected;
    },
    isManualControlEnabled(state) {
      return MANUAL_CONTROL_STATES.includes(state.machineState.id);
    },
  },
  actions: {
    connect() {},
    updateConnection({ commit }) {
      return new Promise((resolve, reject) => {
        api
          .get("/connection")
          .then((response) => {
            commit("updateCurrentConnetion", response.data.current);
            commit("updateConnectionOptions", response.data.options);
            resolve(response.data);
          })
          .catch((error) => {
            console.error(error);
            reject(error);
          });
      });
    },
    updateDevices({ commit }) {
      return new Promise((resolve, reject) => {
        api
          .get("/devices")
          .then((response) => {
            commit("updateDevices", response.data);
            resolve(response.data);
          })
          .catch((error) => {
            console.error(error);
            reject(error);
          });
      });
    },
  },
};
