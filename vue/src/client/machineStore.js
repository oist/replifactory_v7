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
  },
  mutations: {
    updateConnectionOptions(state, options) {
      state.connection.options = options;
    },
    updateCurrentConnetion(state, connection) {
      state.connection.current = connection;
    },
    updateMachineState(state, machineState) {
      state.machineState = machineState
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
  },
};
