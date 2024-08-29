<template>
  <router-view />
</template>

<script>
import { mapState } from "vuex";

export default {
  data() {
    return {
      selectedExperimentClass: undefined,
    };
  },
  computed: {
    ...mapState("experiment", ["experimentClassesOptions"]),
    isExperimentRunning() {
      return false;
    },
    experimentTitle() {
      return this.selectedExperiment
        ? this.selectedExperiment.title
        : "Untitiled Experiment";
    },
  },
  watch: {
    experimentClassesOptions: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.selectedExperimentClass = Object.keys(newVal)[0];
        }
      },
    },
  },
  methods: {
    getExperimentClassesOptions() {
      this.$store
        .dispatch("experiment/getExperimentsClassesOptions")
        .catch((err) => {
          this.$store.dispatch("notifyWarning", {
            content: err.response.data,
          });
        });
    },
    startExperiment() {
      this.sendExperimentCommand("start");
    },
    stopExperiment() {
      this.sendExperimentCommand("stop");
    },
    pauseExperiment() {
      this.sendExperimentCommand("pause");
    },
    resumeExperiment() {
      this.sendExperimentCommand("resume");
    },
    sendExperimentCommand(command, args) {
      const data = {
        experimentId: this.selectedExperimentClass,
        command: command,
        ...args,
      };
      this.$store
        .dispatch("experiment/experimentCommand", data)
        .catch((err) => {
          const message = err.response.data.error || err.response.data;
          this.$store.dispatch("notifyWarning", {
            content: message,
          });
        });
    },
  },
};
</script>
