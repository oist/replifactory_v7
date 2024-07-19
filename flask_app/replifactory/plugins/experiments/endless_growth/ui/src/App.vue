<script setup>
import ExperimentDescription from "./components/ExperimentDescription.vue";
import ExperimentParameters from "./components/ExperimentParameters.vue";
import ExperimentDashboard from "./components/ExperimentDashboard.vue";

import { onMounted, computed } from "vue";
import { useStore } from "vuex";

const store = useStore();

const experimentId = "d82a117c";
const experiment = computed(() => store.getters["experiment/getExperiment"](experimentId));

onMounted(() => {
  store.dispatch("experiment/fetchExperiment", experimentId)
})

</script>

<template>
  <section class="container-fluid">
    <div class="row">
      <h1>Experiment Description</h1>
      <hr />
      <ExperimentDescription />
    </div>
    <div class="row">
      <h1>Experiment Parameters</h1>
      <hr />
      <ExperimentParameters />
    </div>
    <div class="row">
      <h1>Experiment Dashboard</h1>
      <hr />
      <ExperimentDashboard :experiment-data=experiment />
    </div>
  </section>
</template>

<style scoped></style>
