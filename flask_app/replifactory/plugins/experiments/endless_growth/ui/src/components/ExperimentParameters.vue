<template>
  <section>
    <h3>Global Parameters</h3>
    <form>
      <div class="row mb-3">
        <label for="inputCycleTime" class="col-sm-2 col-form-label"
          >Cycle time</label
        >
        <div class="col-auto">
          <div class="input-group mb-3">
            <input
              id="inputCycleTime"
              v-model.number="cycleTime"
              type="number"
              class="form-control"
              aria-label="Cycle time"
              aria-describedby="inputCycleTimeUnit"
              @change="emitUpdate"
            />
            <span id="inputCycleTimeUnit" class="input-group-text"
              >seconds</span
            >
          </div>
        </div>
      </div>
    </form>
    <h3>Reactors parameters</h3>
    <form>
      <div class="row mb-2 g-2">
        <div class="col-sm-4 col-form-label">
          <strong>Enabled</strong>
        </div>
        <div
          v-for="reactor in reactors"
          :key="reactor.index"
          class="col-12 col-sm-1"
        >
          <div>
            <input
              :id="`inputEnabled-${reactor.index}`"
              v-model="reactor.enabled"
              class="form-check-input"
              type="checkbox"
              @change="emitUpdate"
            />
            <label
              class="form-check-label mx-1"
              :for="`inputEnabled-${reactor.index}`"
              >Reactor {{ reactor.index }}</label
            >
          </div>
        </div>
      </div>
      <div class="row mb-2 g-2">
        <div class="col-sm-4 col-form-label">
          <strong>Dilution Threshold</strong>
          <div id="passwordHelpBlock" class="form-text">
            An optical density value which triggers the dilution process in the
            reactor.
          </div>
        </div>
        <div
          v-for="reactor in reactors"
          :key="reactor.index"
          class="col-12 col-sm-1"
        >
          <div class="form-floating">
            <input
              :id="`inputOdDilutionThreshold-${reactor.index}`"
              v-model.number="reactor.threshold"
              type="number"
              class="form-control"
              :aria-label="`OD Dilution Threshold for Reactor ${reactor.index}`"
              :disabled="!reactor.enabled"
              @change="emitUpdate"
            />
            <label :for="`inputOdDilutionThreshold-${reactor.index}`"
              >Reactor {{ reactor.index }}</label
            >
          </div>
        </div>
      </div>
      <div class="row mb-2 g-2">
        <div class="col-sm-4 col-form-label">
          <strong>Dilution Target OD</strong>
        </div>
        <div
          v-for="reactor in reactors"
          :key="reactor.index"
          class="col-12 col-sm-1"
        >
          <div class="form-floating">
            <input
              :id="`inputDilutionTargetOD-${reactor.index}`"
              v-model.number="reactor.targetOD"
              type="number"
              class="form-control"
              :aria-label="`Dilution Target OD for Reactor ${reactor.index}`"
              :disabled="!reactor.enabled"
              @change="emitUpdate"
            />
            <label :for="`inputDilutionTargetOD-${reactor.index}`"
              >Reactor {{ reactor.index }}</label
            >
          </div>
        </div>
      </div>
      <div class="row mb-2 g-2">
        <div class="col-sm-4 col-form-label">
          <strong>Dilution Volume (mL)</strong>
        </div>
        <div
          v-for="reactor in reactors"
          :key="reactor.index"
          class="col-12 col-sm-1"
        >
          <div class="form-floating">
            <input
              :id="`inputDilutionVolume-${reactor.index}`"
              v-model.number="reactor.volume"
              type="number"
              class="form-control"
              :aria-label="`Dilution Volume for Reactor ${reactor.index}`"
              :disabled="!reactor.enabled"
              @change="emitUpdate"
            />
            <label :for="`inputDilutionVolume-${reactor.index}`"
              >Reactor {{ reactor.index }}</label
            >
          </div>
        </div>
      </div>
    </form>
  </section>
</template>

<script setup>
import { ref, defineEmits, onBeforeMount } from "vue";
const emit = defineEmits(["updateParameters"]);

const cycleTime = ref(60 * 4);
const reactors = ref(
  Array(8)
    .fill(null)
    .map((_, index) => ({
      index: index + 1,
      enabled: false,
      volume: 1.0,
      threshold: 0.8,
      targetOD: 0.3,
    })),
);

const emitUpdate = () => {
  const enabledReactors = reactors.value
    .filter((reactor) => reactor.enabled)
    .map(({ enabled, ...rest }) => rest); // Exclude the 'enabled' property;
  emit("updateParameters", {
    cycleTime: cycleTime.value,
    reactors: enabledReactors,
  });
};

onBeforeMount(() => {
  emitUpdate();
});
</script>
