import api from "@/api";

export default {
  namespaced: true,
  state: {
    experimentClassesOptions: {},
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
    updateExperimentsClassesOptions(state, data) {
      state.experimentClassesOptions = data;
    },
    updateExperimentStatus(state, data) {
      state.experiments[data.experiment_id] = data;
    }
  },
  actions: {
    getExperimentsClassesOptions({ commit }) {
      return new Promise((resolve, reject) => {
        api
          .get("/api/experiments")
          .then((response) => {
            commit("updateExperimentsClassesOptions", response.data);
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
