<script setup>
import ExperimentDescription from "./components/ExperimentDescription.vue";
import ExperimentParameters from "./components/ExperimentParameters.vue";
import ExperimentDashboard from "./components/ExperimentDashboard.vue";
</script>

<template>
  <section>
    <h1>Experiment Description</h1>
    <hr />
    <ExperimentDescription />
    <h1>Experiment Parameters</h1>
    <hr />
    <ExperimentParameters />
    <h1>Experiment Dashboard</h1>
    <hr />
    <ExperimentDashboard />
  </section>
</template>

<style scoped></style>
