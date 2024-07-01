<template>
  <div v-if="hasRunningExperiments" class="list-group">
    <div
      v-for="(status, id) in experimentStatuses"
      :key="id"
      class="list-group-item"
    >
      <div class="d-flex w-100 justify-content-between">
        <h5 class="mb-1">{{ status.name }}</h5>
        <small>{{ timeSinceStart(status.startTime) }}</small>
      </div>
      <p class="mb-1">{{ status.status }}</p>
      <small
        >Cycles: {{ status.cycles }} next every
        {{ status.cycleTime }} seconds.</small
      >
    </div>
  </div>
  <div class="text-end my-2">
    <button class="btn btn-success" @click="goToExperimentSection">
      <CIcon icon="cilPlus" /> Run new experiment
    </button>
  </div>
</template>

<script>
import { CIcon } from "@coreui/icons-vue";
export default {
  components: {
    CIcon,
  },
  data() {
    return {
      updateIntervalId: null,
    };
  },
  computed: {
    experimentStatuses() {
      return this.$store.state.experiment.experiments;
    },
    hasRunningExperiments() {
      return Object.keys(this.experimentStatuses).length > 0;
    },
  },
  mounted() {
    this.updateIntervalId = setInterval(() => {
      this.updateTimeSinceStart();
    }, 5000);
  },
  beforeUnmount() {
    if (this.updateIntervalId) {
      clearInterval(this.updateIntervalId);
    }
  },
  created() {
    this.$store.dispatch("experiment/getExperiments");
  },
  methods: {
    goToExperimentSection() {
      this.$router.push({ name: "NewExperiment" });
    },
    timeSinceStart(startTime) {
      const start = new Date(startTime);
      const now = new Date();
      const diffInSeconds = Math.floor((now - start) / 1000);
      const hours = Math.floor(diffInSeconds / 3600);
      const minutes = Math.floor((diffInSeconds % 3600) / 60);
      const seconds = diffInSeconds % 60;

      return `${hours}h ${minutes}m ${seconds}s ago`;
    },
    updateTimeSinceStart() {
      // Update logic for time since start or any other data that needs refreshing
      // This could involve recalculating the time since start for each experiment
      // and updating the experimentStatuses data accordingly
    },
  },
};
</script>
