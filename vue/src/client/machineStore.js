import api from "@/api.js";

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
    data: {
      state: {
        flags: {
          closedOrError: true,
        },
        text: "Offline",
      },
      devices: {},
    },
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
    updateData(state, data) {
      state.data = data;
    },
  },
  getters: {
    isDisconnected(state) {
      return state.data.state.flags.closedOrError;
    },
    isConnected(state, getters) {
      return !getters.isDisconnected;
    },
    isManualControlEnabled(state) {
      return state.data.state.flags.manualControl;
    },
    getDeviceById: (state) => (id) => {
      return Object.hasOwn(state.data.devices, id) ? state.data.devices[id] : {}
    }
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
    runCommand(context, payload) {
      const { device, deviceId, command, ...args } = payload;
      const endpoint = `/machine/${device}`;
      return new Promise((resolve, reject) => {
        api
          .post(endpoint, { deviceId, command, ...args })
          .then((response) => {
            resolve(response.data);
          })
          .catch((error) => {
            console.error(`Error updating ${deviceId} state:`, error);
            reject(error);
          });
      });
    },
  },
};
