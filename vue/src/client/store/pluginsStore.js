import api from "@/api.js";

export default {
  namespaced: true,
  state: {
    pluginsMeta: [],
  },
  mutations: {
    setPluginsMeta(state, payload) {
      state.pluginsMeta = payload;
    },
  },
  getters: {
    getPlugin: (state) => (id) => {
      return state.pluginsMeta.find((plugin) => plugin.id === id);
    },
    getExperimentsPlugins(state) {
      return state.pluginsMeta.filter((plugin) => plugin.kind === "experiment");
    },
  },
  actions: {
    fetchPluginsMeta({ commit }) {
      return new Promise((resolve, reject) => {
        api
          .get("/api/plugins")
          .then((response) => {
            commit("setPluginsMeta", response.data);
            resolve(response.data);
          })
          .catch((error) => {
            console.log(error);
            let errorMessage = "Failed to fetch plugins meta";
            if (error.response && error.response.data) {
              errorMessage = error.response.data.message || error.response.data;
            }
            reject(errorMessage);
          });
      });
    },
  },
};
