const ExperimentDescription = () =>
  import("./components/ExperimentDescription.vue");
const ExperimentParameters = () =>
  import("./components/ExperimentParameters.vue");

const MyPlugin = {
  install(Vue, options) {
    Vue.component("ExperimentDescription", ExperimentDescription);
    Vue.component("ExperimentParameters", ExperimentParameters);
  },
};

export default MyPlugin;
