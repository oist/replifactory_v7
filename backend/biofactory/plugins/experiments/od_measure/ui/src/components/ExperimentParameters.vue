<script setup></script>

<template>
  <section class="container">
    <h3 class="custom-color">Global Parameters</h3>
    <form>
      <div class="row mb-3">
        <label for="inputCycleTime" class="col-sm-2 col-form-label"
          >Cycle time</label
        >
        <div class="col-auto">
          <div class="input-group mb-3">
            <input
              id="inputCycleTime"
              type="number"
              class="form-control"
              aria-label="Cycle time"
              aria-describedby="inputCycleTimeUnit"
              :value="60 * 4"
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
        <div v-for="n in 8" :key="n" class="col-12 col-sm-1">
          <div>
            <input
              :id="`inputEnabled-${n}`"
              class="form-check-input"
              type="checkbox"
              checked
            />
            <label class="form-check-label mx-1" :for="`inputEnabled-${n}`"
              >Reactor {{ n }}</label
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
        <div v-for="n in 8" :key="n" class="col-12 col-sm-1">
          <div class="form-floating">
            <input
              :id="`inputOdDilutionThreshold-${n}`"
              type="number"
              class="form-control"
              :aria-label="`OD Dilution Threshold for Reactor ${n}`"
              :value="0.8"
            />
            <label :for="`inputOdDilutionThreshold-${n}`"
              >Reactor {{ n }}</label
            >
          </div>
        </div>
      </div>
      <div class="row mb-2 g-2">
        <div class="col-sm-4 col-form-label">
          <strong>Dilution Target OD</strong>
        </div>
        <div v-for="n in 8" :key="n" class="col-12 col-sm-1">
          <div class="form-floating">
            <input
              :id="`inputDilutionTargetOD-${n}`"
              type="number"
              class="form-control"
              :aria-label="`Dilution Target OD for Reactor ${n}`"
              :value="0.3"
            />
            <label :for="`inputDilutionTargetOD-${n}`">Reactor {{ n }}</label>
          </div>
        </div>
      </div>
      <div class="row mb-2 g-2">
        <div class="col-sm-4 col-form-label">
          <strong>Dilution Volume (mL)</strong>
        </div>
        <div v-for="n in 8" :key="n" class="col-12 col-sm-1">
          <div class="form-floating">
            <input
              :id="`inputDilutionVolume-${n}`"
              type="number"
              class="form-control"
              :aria-label="`Dilution Volume for Reactor ${n}`"
              :value="1.0"
            />
            <label :for="`inputDilutionVolume-${n}`">Reactor {{ n }}</label>
          </div>
        </div>
      </div>
    </form>
  </section>
</template>

<style scoped>
.custom-color {
  color: #6f42c1;
}
</style>
