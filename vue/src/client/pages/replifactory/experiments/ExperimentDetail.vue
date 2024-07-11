<script setup>
import {
  ref,
  shallowRef,
  markRaw,
  onBeforeMount,
  onBeforeUnmount,
  defineAsyncComponent,
  computed,
} from "vue";
import { useStore } from "vuex";
import { useRouter, useRoute } from "vue-router";
import { componentLoader } from "@/plugins.js";
import { CIcon } from "@coreui/icons-vue";

const store = useStore();
const route = useRoute();
const router = useRouter();

const timeSpent = ref("");
const intervalId = ref(null);
const dashboardComponent = shallowRef(
  markRaw({
    template: "<div>Loading dashboard...</div>",
  }),
);
const experiment = computed(() =>
  store.getters["experiment/getExperiment"](route.params.id),
);
const localStartTime = computed(() => {
  return convertUTCtoLocalDate(experiment.value.startTime);
});
const localEndTime = computed(() => {
  return convertUTCtoLocalDate(experiment.value.endTime);
});

function convertUTCtoLocalDate(utcDate) {
  if (!utcDate) return "";
  const date = new Date(utcDate);
  return date.toLocaleString();
}

onBeforeMount(async () => {
  const experimentId = route.params.id;
  store
    .dispatch("experiment/getExperiment", experimentId)
    .then((exp) => {
      calculateTimeSpent();
      if (!exp.endTime) {
        intervalId.value = setInterval(calculateTimeSpent, 1000);
      }
      const module = store.getters["plugins/getUiModuleForClass"](
        exp.class,
        "dashboard",
      );
      if (!module) {
        console.error("Dashboard component not found for the experiment");
        return;
      }
      dashboardComponent.value = defineAsyncComponent({
        loader: componentLoader(module.path),
      });
    })
    .catch((error) => {
      console.error(error);
    });
});
onBeforeUnmount(() => {
  if (intervalId.value) {
    clearInterval(intervalId.value);
  }
});

const goBack = () => {
  router.back();
};

function calculateTimeSpent() {
  if (!experiment.value) {
    console.log("Experiment data is not available yet.");
    return;
  }
  const startTime = new Date(experiment.value.startTime).getTime();
  const currentTime = experiment.value.endTime
    ? new Date(experiment.value.endTime).getTime()
    : Date.now();
  const difference = currentTime - startTime;
  // Convert difference from milliseconds to a more readable format
  // Example: HH:MM:SS
  timeSpent.value = new Date(difference).toISOString().substring(11, 11 + 8);
}
</script>

<template>
  <div class="container py-2 bg-body">
    <button class="btn btn-secondary" @click="goBack">
      <CIcon icon="cilArrowLeft" /> Go Back
    </button>
    <div v-if="experiment" class="row">
      <h1>{{ experiment.name }}</h1>
      <div class="mb-1 text-body-secondary">
        Started on {{ localStartTime }}
      </div>
      <h2>Status</h2>
      <div class="d-flex gap-2 justify-content-start py-1 fs-3">
        <span
          v-if="experiment.alive"
          class="badge d-flex align-items-center p-1 pe-2 text-success-emphasis bg-success-subtle border border-success-subtle rounded-pill"
        >
          <CIcon icon="cilWalk" size="xl" /> Alive
        </span>
        <span
          v-if="experiment.interrupted"
          class="badge d-flex align-items-center p-1 pe-2 text-warning-emphasis bg-warning-subtle border border-warning-subtle rounded-pill"
        >
          <i class="bi bi-x-octagon me-1"></i> Interrupted
        </span>
        <span
          class="badge d-flex align-items-center p-1 pe-2 text-light-emphasis bg-light-subtle border border-light-subtle rounded-pill"
        >
          <i class="bi bi-arrow-repeat me-1"></i> {{ experiment.cycles }}
        </span>
      </div>
      <h2>Details</h2>
      <div class="row">
        <div class="col-md-2 text-primary">Start time</div>
        <div class="col-md-3 text-end">
          {{ localStartTime }}
        </div>
      </div>
      <div class="row">
        <div class="col-md-2 text-primary">End time</div>
        <div class="col-md-3 text-end">
          {{ localEndTime }}
        </div>
      </div>
      <div class="row">
        <div class="col-md-2 text-primary">Time spent</div>
        <div class="col-md-3 text-end">
          {{ timeSpent }}
        </div>
      </div>
      <div class="row">
        <div class="col-md-2 text-primary">Status</div>
        <div class="col-md-3 text-end">
          {{ experiment.status }}
        </div>
      </div>
    </div>
    <h2>Dashboard</h2>
    <component :is="dashboardComponent" />
  </div>
</template>
