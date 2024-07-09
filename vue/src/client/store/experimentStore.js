import api from "@/api";

export default {
  namespaced: true,
  state: {
    experiments: {},

    // hostname: "replifactory_GUI",
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
  mutations: {
    updateExperimentStatus(state, data) {
      state.experiments[data.experiment_id] = data;
    },
    updateExperimentsStatuses(state, data) {
      state.experiments = data;
    },
  },
  actions: {
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
    startExperiment(context, payload) {
      return new Promise((resolve, reject) => {
        api
          .post("/api/experiments", { ...payload })
          .then((response) => {
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
