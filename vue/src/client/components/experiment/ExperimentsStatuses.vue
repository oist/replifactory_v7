<template>
  <div v-if="hasRunningExperiments" class="list-group">
    <div
      v-for="(status, id) in experimentStatuses"
      :key="id"
      class="list-group-item"
    >
      <div class="d-flex w-100 justify-content-between">
        <div>
          <h5 class="mb-1">{{ status.name }}</h5>
          <p class="mb-1">{{ status.status }}</p>
          <small
            >Cycles: {{ status.cycles }} next every
            {{ status.cycleTime }} seconds.</small
          >
        </div>
        <div class="d-flex flex-column justify-content-start">
          <div>
            <small>{{ timeSinceStart(status.startTime) }}</small>
          </div>
          <div class="text-end">
            <div
              v-if="status.alive"
              class="btn-group"
              role="group"
              aria-label="Basic example"
            >
              <!-- <button class="btn btn-warning" @click="sendCommand(experiment.id, experiment.status)">
                <CIcon icon="cilMediaPause" />
              </button> -->
              <button class="btn btn-danger" @click="showStopModal(id)">
                <CIcon icon="cilMediaStop" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="text-end my-2">
    <button class="btn btn-success" @click="goToExperimentSection">
      <CIcon icon="cilPlus" /> Run new experiment
    </button>
  </div>
  <BModal
    id="stopModal"
    v-model="stopModal"
    title="Stop Experiment"
  >
    <template #modal-header="{ close }">
      <h5 class="modal-title">Stop Experiment</h5>
      <button type="button" class="btn-close" @click="close"></button>
    </template>

    <div>Are you sure you want to stop the experiment?</div>

    <template #footer>
      <button
        type="button"
        class="btn btn-secondary"
        @click="stopModal = false"
      >
        Leave
      </button>
      <button type="button" class="btn btn-danger" @click="confirmStop">
        Stop
      </button>
    </template>
  </BModal>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";
import { CIcon } from "@coreui/icons-vue";
import { BModal } from "bootstrap-vue-next";

const store = useStore();
const router = useRouter();

const updateIntervalId = ref(null);
const selectedExperimentId = ref(null);
const stopModal = ref(false);

const experimentStatuses = computed(() => store.state.experiment.experiments);
const hasRunningExperiments = computed(
  () => Object.keys(experimentStatuses.value).length > 0,
);

onMounted(() => {
  updateIntervalId.value = setInterval(() => {
    updateTimeSinceStart();
  }, 5000);
  store.dispatch("experiment/getExperiments");
});
onBeforeUnmount(() => {
  if (updateIntervalId.value) {
    clearInterval(updateIntervalId.value);
  }
});

function goToExperimentSection() {
  router.push({ name: "NewExperiment" });
}

function timeSinceStart(startTime) {
  const start = new Date(startTime);
  const now = new Date();
  const diffInSeconds = Math.floor((now - start) / 1000);
  const hours = Math.floor(diffInSeconds / 3600);
  const minutes = Math.floor((diffInSeconds % 3600) / 60);
  const seconds = diffInSeconds % 60;

  return `${hours}h ${minutes}m ${seconds}s ago`;
}

function updateTimeSinceStart() {
  // Implementation of updateTimeSinceStart
  // This function needs to be defined or updated to work with the refactored code
}
const showStopModal = (experimentId) => {
  selectedExperimentId.value = experimentId;
  stopModal.value = true;
};
function confirmStop() {
  sendExperimentCommand(selectedExperimentId.value, "stop", {});
  stopModal.value = false;
}
function sendExperimentCommand(experimentId, command, args) {
  const data = {
    experimentId: experimentId,
    command: command,
    ...args,
  };
  store.dispatch("experiment/experimentCommand", data).catch((err) => {
    const message = err.response.data.error || err.response.data;
    store.dispatch("notifyWarning", {
      content: message,
    });
  });
}
</script>
