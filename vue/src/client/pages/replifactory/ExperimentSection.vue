<template>
  <!-- <div class="container">
    <div class="card">
      <div class="card-body">
        <h5 class="card-title">{{ experimentTitle }}</h5>
        <form>
          <div class="row mb-3">
            <label for="experimentClassSelect" class="col-sm-2 col-form-label"
              >Choise experiment class</label
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
                    v-for="(value, id) in experimentClassesOptions"
                    :key="id"
                    :value="id"
                  >
                    {{ value }} ({{ id }})
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
        <component
          :is="selectedExperiment.description"
          v-if="selectedExperiment"
        ></component>
        <component
          :is="selectedExperiment.parameters"
          v-if="selectedExperiment"
        ></component>
        <component
          :is="selectedExperiment.dashboard"
          v-if="selectedExperiment"
        ></component>
      </div>
    </div>
  </div> -->
  <router-view />
</template>

<script>
// import { CFormSelect, CInputGroup, CButton } from "@coreui/vue";
import { mapState } from "vuex";
// import EndlessGrowth from "@/client/components/ExperimentTab/experiments/EndlessGrowth";

export default {
  // components: {
  //   CFormSelect,
  //   CInputGroup,
  //   CButton,
  // },
  data() {
    return {
      selectedExperimentClass: undefined,
    };
  },
  computed: {
    ...mapState("experiment", ["experimentClassesOptions"]),
    isExperimentRunning() {
      return false;
    },
    // selectedExperiment() {
    //   switch (this.selectedExperimentClass) {
    //     case "flask_app.replifactory.experiment.endless_growth.EndlessGrowthExperiment":
    //       return EndlessGrowth;
    //     // case "flask_app.replifactory.experiment.MorbidostatExperiment":
    //     //   return Morbidostat;
    //     default:
    //       return null;
    //   }
    // },
    experimentTitle() {
      return this.selectedExperiment
        ? this.selectedExperiment.title
        : "Untitiled Experiment";
    },
  },
  watch: {
    experimentClassesOptions: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.selectedExperimentClass = Object.keys(newVal)[0];
        }
      },
    },
  },
  // created() {
  //   this.getExperimentClassesOptions();
  // },
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
