<script setup>
import ExperimentDescription from "./components/ExperimentDescription.vue";
import ExperimentParameters from "./components/ExperimentParameters.vue";
import ExperimentDashboard from "./components/ExperimentDashboard.vue";
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
      <ExperimentDashboard />
    </div>
  </section>
</template>

<style scoped></style>
