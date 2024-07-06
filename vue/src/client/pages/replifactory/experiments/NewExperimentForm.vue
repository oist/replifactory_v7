<template>
  <div class="container d-flex align-items-stretch">
    <div class="card w-100">
      <div class="card-body">
        <h5 class="card-title">{{ experimentTitle }}</h5>
        <form>
          <div class="row mb-3">
            <label for="experimentClassSelect" class="col-sm-2 col-form-label"
              >Choose an experiment</label
            >
            <div class="col-sm-10">
              <CInputGroup>
                <CFormSelect
                  id="experimentClassSelect"
                  v-model="selectedExperimentClass"
                  aria-label="Select experiment class"
                  :disabled="isExperimentRunning"
                >
                  <option
                    v-for="(value, id) in modifiedExperimentClassesOptions"
                    :key="id"
                    :value="id"
                  >
                    {{ value }}
                  </option>
                </CFormSelect>
                <CButton
                  type="button"
                  color="success"
                  variant="outline"
                  @click="startExperiment"
                  >Start</CButton
                >
                <CButton
                  type="button"
                  color="warning"
                  variant="outline"
                  @click="pauseExperiment"
                  >Pause</CButton
                >
                <CButton
                  type="button"
                  color="danger"
                  variant="outline"
                  @click="stopExperiment"
                  >Stop</CButton
                >
              </CInputGroup>
            </div>
          </div>
        </form>
        <!-- <CustomDynamicComponent :url="descriptionComponent" /> -->
        <component :is="descriptionComponent" />
        <component :is="parametersComponent" />
        <!-- <CustomDynamicComponent :url="parametersComponent" /> -->
      </div>
    </div>
  </div>
</template>

<script>
import { CFormSelect, CInputGroup, CButton } from "@coreui/vue";
import { mapState } from "vuex";
import { defineAsyncComponent } from "vue";
import { componentLoader } from "@/plugins.js";
// import DynamicComponent from "@/client/components/DynamicComponent.vue";
// import CustomDynamicComponent from "@/client/components/CustomDynamicComponent.vue";
// import EndlessGrowth from "@/client/components/ExperimentTab/experiments/EndlessGrowth";

export default {
  components: {
    CFormSelect,
    CInputGroup,
    CButton,
    // DynamicComponent,
    // CustomDynamicComponent,
  },
  data() {
    return {
      selectedExperimentClass: undefined,
    };
  },
  computed: {
    ...mapState("experiment", ["experimentClassesOptions"]),
    modifiedExperimentClassesOptions() {
        return {
            none: "Select an option...",
            ...this.experimentClassesOptions,
        };
    },
    isExperimentRunning() {
      return false;
    },
    selectedExperiment() {
      switch (this.selectedExperimentClass) {
        case "flask_app.replifactory.plugins.experiments.endless_growth.plugin.EndlessGrowthExperiment":
          return {
            description: defineAsyncComponent({
                loader: componentLoader("/plugins/flask_app.replifactory.plugins.experiments.endless_growth.plugin.EndlessGrowthExperimentPlugin/endless-growth-experiment-description.umd.cjs"),
            }),
            parameters: defineAsyncComponent({
                loader: componentLoader("/plugins/flask_app.replifactory.plugins.experiments.endless_growth.plugin.EndlessGrowthExperimentPlugin/endless-growth-experiment-parameters.umd.cjs"),
            }),
          };
        case "flask_app.replifactory.plugins.experiments.od_measure.plugin.ODMeasureExperiment":
          return {
            description: defineAsyncComponent({
                loader: componentLoader("/plugins/flask_app.replifactory.plugins.experiments.od_measure.plugin.ODMeasureExperimentPlugin/od-measure-experiment-description.umd.min.js"),
            }),
            parameters: defineAsyncComponent({
                loader: componentLoader("/plugins/flask_app.replifactory.plugins.experiments.od_measure.plugin.ODMeasureExperimentPlugin/od-measure-experiment-parameters.umd.min.js"),
            }),
          };
        default:
          return {
            description: {template: " "},
            parameters: {template: " "},
          };
      }
    },
    descriptionComponent() {
        return this.selectedExperiment.description;
    },
    parametersComponent() {
        return this.selectedExperiment.parameters;
    },
    experimentTitle() {
      return this.selectedExperiment
        ? this.selectedExperiment.title
        : "Untitiled Experiment";
    },
  },
  watch: {
    // experimentClassesOptions: {
    //   immediate: true,
    //   handler(newVal) {
    //     if (newVal) {
    //       this.selectedExperimentClass = Object.keys(newVal)[0];
    //     }
    //   },
    // },
  },
  created() {
    this.getExperimentClassesOptions();
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
