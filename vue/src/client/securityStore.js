import api from "@/api.js";

export default {
  namespaced: true,
  state: {
    user: {
      permissions: [],
      email: "",
    },
    authorized: false,
    token: "",
  },
  mutations: {
    setUserData(state, userData) {
      state.user = userData;
    },
    setToken(state, token) {
      state.token = token;
    },
    setAuthorized(state, authorized) {
      state.authorized = authorized;
    },
  },
  getters: {
    authorized(state) {
      return state.authorized;
    },
  },
  actions: {
    connect() {},
    login({ commit }, userData) {
      return new Promise((resolve, reject) => {
        api
          .post("/security/login", userData)
          .then((response) => {
            commit("setAuthorized", true);
            resolve(response);
          })
          .catch((error) => {
            commit("setAuthorized", false);
            console.error(error);
            reject(error);
          });
      });
    },
    verify({ commit }) {
      return new Promise((resolve, reject) => {
        api
          .get("/api/security/verify")
          .then((response) => {
            if (response.status === 200) {
              commit("setAuthorized", true);
            }
            resolve(response);
          })
          .catch((error) => {
            commit("setAuthorized", false);
            console.error(error);
            reject(error);
          });
      });
    },
  },
};
