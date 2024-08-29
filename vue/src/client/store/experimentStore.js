import api from "@/api";

export default {
  namespaced: true,
  state: {
    experiments: {},

    // hostname: "biofactory_GUI",
    // errorMessage: null,
    // experiments: [],
    // currentExperiment: {
    //   id: null,
    //   name: null,
    //   parameters: null,
    //   data: {},
    // },
    // plot_data: {
    //   1: null,
    //   2: null,
    //   3: null,
    //   4: null,
    //   5: null,
    //   6: null,
    //   7: null,
    // },
  },
  getters: {
    getExperiment: (state) => (id) => {
      return state.experiments[id];
    },
  },
  mutations: {
    updateExperimentStatus(state, { id, data }) {
      state.experiments[id] = data;
    },
    updateExperimentsStatuses(state, data) {
      state.experiments = data;
    },
  },
  actions: {
    getExperiment({ commit }, experimentId) {
      return new Promise((resolve, reject) => {
        api
          .get("/api/experiments/" + experimentId)
          .then((response) => {
            commit("updateExperimentStatus", {
              id: experimentId,
              data: response.data,
            });
            resolve(response.data);
          })
          .catch((error) => {
            console.error(error);
            reject(error);
          });
      });
    },
    getExperiments({ commit }) {
      return new Promise((resolve, reject) => {
        api
          .get("/api/experiments")
          .then((response) => {
            commit("updateExperimentsStatuses", response.data);
            resolve(response.data);
          })
          .catch((error) => {
            console.error(error);
            reject(error);
          });
      });
    },
    startExperiment({ commit }, payload) {
      return new Promise((resolve, reject) => {
        api
          .post("/api/experiments", { ...payload })
          .then((response) => {
            commit("updateExperimentStatus", { id: response.data.id, data: response.data });
            resolve(response.data);
          })
          .catch((error) => {
            console.error(error);
            reject(error);
          });
      });
    },
    experimentCommand(context, payload) {
      const { experimentId, command, ...args } = payload;
      const endpoint = `/api/experiments/${experimentId}/${command}`;
      return new Promise((resolve, reject) => {
        api
          .post(endpoint, { ...args })
          .then((response) => {
            resolve(response.data);
          })
          .catch((error) => {
            console.error(`Error updating ${experimentId} state:`, error);
            reject(error);
          });
      });
    },
  },
};
