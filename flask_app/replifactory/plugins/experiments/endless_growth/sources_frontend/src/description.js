const ExperimentDescription = () =>
  import("./components/ExperimentDescription.vue");

const MyPlugin = {
    install(Vue, options) {
      Vue.component('ExperimentDescription', ExperimentDescription);
    }
  };

  export default MyPlugin;