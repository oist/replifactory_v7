<template>
  <CToast
    v-if="errorMessage"
    :autohide="true"
    :fade="true"
    @hidden="clearErrorMessage"
  >
    <CToastHeader close-button> Error </CToastHeader>
    <CToastBody>
      {{ errorMessage }}
    </CToastBody>
  </CToast>

  <div class="experiment-setup">
    <div class="d-flex">
      <CFormFloating class="flex-grow-1 mt-3">
        <CFormSelect
          id="floatingSelect"
          v-model="currentExperimentId"
          floating-label="Select Experiment"
          aria-label="Floating label select example"
          @change="handleExperimentSelected"
        >
          <option
            v-for="experiment in reversedExperiments"
            :key="experiment.id"
            :value="experiment.id"
          >
            {{ experiment.name }}
          </option>
        </CFormSelect>
      </CFormFloating>
      <CButton
        color="primary"
        class="mt-3 ml-3"
        @click="handleNewExperimentButton"
      >
        +
      </CButton>

      <div class="button-container flex-grow-1 ml-5 d-flex align-items-stretch">
        <CButton
          class="mt-3 ml-3 flex-grow-1 d-flex align-items-center"
          :class="{ active: currentExperiment.status === 'running' }"
          :style="{
            'background-color':
              currentExperiment.status === 'running'
                ? '#28a745'
                : 'transparent',
          }"
          color="success"
          title="Start the experiment loop - measure OD every minute and dilute the cultures as necessary, according to the parameters."
          @click="startExperiment()"
        >
          Start
        </CButton>
        <CButton
          class="mt-3 ml-3 flex-grow-1 d-flex align-items-center"
          :class="{ active: currentExperiment.status === 'paused' }"
          :style="{
            'background-color':
              currentExperiment.status === 'paused' ? '#ffc107' : 'transparent',
          }"
          title="Pause the dilutions, but keep measuring the OD every minute."
          color="warning"
          @click="pauseExperiment()"
        >
          Pause
        </CButton>
        <CButton
          class="mt-3 ml-3 flex-grow-1 d-flex align-items-center"
          :class="{ active: currentExperiment.status === 'stopped' }"
          :style="{
            'background-color':
              currentExperiment.status === 'stopped'
                ? '#dc3545'
                : 'transparent',
          }"
          color="danger"
          title="Stop gracefully - wait for the current dilution to finish."
          @click="stopExperiment()"
          @dblclick="forceStopExperiment()"
        >
          Stop
        </CButton>
      </div>
    </div>

    <div v-if="showCreate" class="d-flex">
      <CFormFloating v-if="showCreate" class="flex-grow-1 mt-3">
        <CFormInput
          id="floatingInput"
          :model-value="newExperimentname"
          floating-label="New Experiment Name"
          @update:model-value="(v) => (newExperimentname = v)"
        />
      </CFormFloating>

      <CButton
        color="success"
        class="ml-3 mt-3"
        @click="createAndSelectExperiment"
      >
        Create Experiment
      </CButton>
    </div>

    <!--      <h3>Current Experiment:</h3>-->
    <!--      <p>{{ currentExperiment.name ?? "No Experiment Selected" }}</p>-->

    <div v-if="currentExperiment">
      <div
        class="experiment-parameters mt-3"
        style="align-items: center; display: flex; flex-direction: column"
      >
        <div
          class="bottle-parameters"
          style="display: flex; flex-direction: row"
        >
          <template
            v-for="(value, key) in currentExperiment.parameters"
            :key="key"
          >
            <CFormFloating v-if="key !== 'cultures'" class="flex-grow-1 ml-3">
              <CFormInput
                :id="`floatingInput_${key}`"
                :class="{ active: currentExperiment.status !== 'running' }"
                :model-value="value"
                :floating-label="`${key}`"
                :placeholder="`Enter ${key}`"
                :readonly="currentExperiment.status === 'running'"
                @update:model-value="
                  (v) => (currentExperiment.parameters[key] = v)
                "
                @change="handleInputChange(key, $event.target.value)"
              />
            </CFormFloating>
          </template>
        </div>

        <CAccordion class="mt-3">
          <CAccordionItem visible="false">
            <CAccordionHeader>
              <CButton block variant="link" color="primary">
                Experiment Culture Parameters
              </CButton>
            </CAccordionHeader>
            <CAccordionBody>
              <div
                v-if="
                  Object.keys(currentExperiment?.parameters?.cultures || {})
                    .length > 0
                "
                class="experiment-cultures mt-3"
              >
                <CRow class="culture-row">
                  <CCol
                    v-for="(culture, index) in currentExperiment.parameters
                      .cultures"
                    :key="index"
                    class="culture-column"
                  >
                    <CultureConfig
                      :experiment="currentExperiment"
                      :vial="index"
                    />
                  </CCol>
                </CRow>
              </div>
            </CAccordionBody>
          </CAccordionItem>
        </CAccordion>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
import {
  CButton,
  CFormFloating,
  CFormInput,
  CFormSelect,
  CRow,
  CCol,
  CToast,
  CToastBody,
  CToastHeader,
  CAccordion,
  CAccordionBody,
  CAccordionHeader,
  CAccordionItem,
} from "@coreui/vue";
import CultureConfig from "./CultureConfig.vue";
// import ExperimentChart from './ExperimentChart.vue';

export default {
  components: {
    // ExperimentChart,
    CultureConfig,

    CButton,
    CFormFloating,
    CFormInput,
    CFormSelect,
    CRow,
    CCol,
    CToast,
    CToastBody,
    CToastHeader,
    CAccordion,
    CAccordionBody,
    CAccordionHeader,
    CAccordionItem,
  },
  data() {
    return {
      newExperimentname: null,
      showCreate: false,
      currentExperimentId: null,
    };
  },
  computed: {
    ...mapState("experiment", [
      "experiments",
      "currentExperiment",
      "errorMessage",
    ]),
    reversedExperiments() {
      return [...this.experiments].reverse(); // Reverse a copy of the original array
    },
  },
  methods: {
    ...mapActions("experiment", [
      "updateExperimentParameters",
      "setCurrentExperimentAction",
      "createExperiment",
      "fetchExperiments",
      "fetchCurrentExperiment",
      "startExperiment",
      "pauseExperiment",
      "stopExperiment",
    ]),
    async handleInputChange(key, value) {
      // Update the experiment parameters with the new input value
      await this.updateExperimentParameters({
        experimentId: this.currentExperiment.id,
        parameters: {
          ...this.currentExperiment.parameters,
          [key]: value,
        },
      });
    },

    async handleNewExperimentButton() {
      this.showCreate = !this.showCreate;
      if (
        this.currentExperiment.status === "running" ||
        this.currentExperiment.status === "paused"
      ) {
        await this.stopExperiment(this.currentExperiment.id);
      }
    },

    async handleExperimentSelected(event) {
      if (
        this.currentExperiment.status === "running" ||
        this.currentExperiment.status === "paused"
      ) {
        await this.stopExperiment(this.currentExperiment.id);
      }
      const selectedExperimentId = event.target.value;
      if (selectedExperimentId !== this.currentExperimentId) {
        this.currentExperimentId = selectedExperimentId;
        await this.setCurrentExperimentAction(this.currentExperimentId);
      }
    },
    async createAndSelectExperiment() {
      //if current experiment exists, copy parameters
      if (this.currentExperiment) {
        this.currentExperimentId = await this.createExperiment({
          name: this.newExperimentname,
          parameters: this.currentExperiment.parameters,
        });
        console.log(
          "created new experiment with same parameters as current experiment",
        );
      } else {
        console.log("created new experiment with default parameters");
        this.currentExperimentId = await this.createExperiment({
          name: this.newExperimentname,
        });
      }
      console.log(this.currentExperimentId);
      await this.handleExperimentSelected({
        target: { value: this.currentExperimentId },
      });
      this.showCreate = false;
      this.newExperimentname = "";
    },
  },
  async created() {
    await this.fetchExperiments();
    await this.fetchCurrentExperiment();
    this.currentExperimentId = this.currentExperiment.id;
  },
};
</script>

<style scoped>
.experiment-setup {
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;
}
.button-container {
  display: flex;
  justify-content: center; /* Align items along the main axis */
  align-items: center; /* Align items along the cross axis */
}
.experiment-cultures {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  width: 1250px;
  margin: 0 auto;
}
</style>
