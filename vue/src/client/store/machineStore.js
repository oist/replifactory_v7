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
    queue: {
      send: {},
      command: {},
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
    updateSendQueue(state, data) {
      state.queue.send = data;
    },
    updateCommandQueue(state, data) {
      state.queue.command = data;
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
      return Object.hasOwn(state.data.devices, id)
        ? state.data.devices[id]
        : {};
    },
  },
  actions: {
    connect() {},
    updateConnection({ commit }) {
      return new Promise((resolve, reject) => {
        api
          .get("/api/connection")
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
          .get("/api/devices")
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
    deviceCommand(context, payload) {
      const { deviceId, command, ...args } = payload;
      const endpoint = `/api/devices/${deviceId}/command`;
      return new Promise((resolve, reject) => {
        api
          .post(endpoint, { command, ...args })
          .then((response) => {
            resolve(response.data);
          })
          .catch((error) => {
            console.error(`Error updating ${deviceId} state:`, error);
            reject(error);
          });
      });
    },
    reactorCommand(context, payload) {
      const { reactorId, ...args } = payload;
      const endpoint = `/api/reactors/${reactorId}/command`;
      return new Promise((resolve, reject) => {
        api
          .post(endpoint, args)
          .then((response) => {
            resolve(response.data);
          })
          .catch((error) => {
            console.error(`Error updating reactor state:`, error);
            reject(error);
          });
      });
    },
    machineCommand(context, payload) {
      const { command, ...args } = payload;
      const endpoint = `/api/machine/command`;
      return new Promise((resolve, reject) => {
        api
          .post(endpoint, { command, ...args })
          .then((response) => {
            resolve(response.data);
          })
          .catch((error) => {
            console.error(`Error updating machine state:`, error);
            reject(error);
          });
      });
    },
  },
};
