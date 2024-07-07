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
                  v-model="selectedExperimentPluginId"
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
import { mapGetters } from "vuex";
import { defineAsyncComponent } from "vue";
import { componentLoader } from "@/plugins.js";

export default {
  components: {
    CFormSelect,
    CInputGroup,
    CButton,
  },
  data() {
    return {
      selectedExperimentPluginId: undefined,
    };
  },
  computed: {
    ...mapGetters("plugins", ["getExperimentsPlugins", "getPlugin"]),
    modifiedExperimentClassesOptions() {
      let options = {
        none: "Select an option...",
      };
      this.getExperimentsPlugins.forEach((plugin) => {
        options[plugin.id] = plugin.name;
      });
      return options;
    },
    isExperimentRunning() {
      return false;
    },
    selectedExperiment() {
      const plugin = this.getPlugin(this.selectedExperimentPluginId);
      if (!plugin) {
        return {
          title: "No experiment selected",
          description: { template: " " },
          parameters: { template: " " },
        };
      }
      let experimentUiComponents = {
        title: plugin.name,
      };
      plugin.ui_modules.forEach((module) => {
        experimentUiComponents[module.kind] = defineAsyncComponent({
          loader: componentLoader(module.path),
        });
      });
      return experimentUiComponents;
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
//   watch: {
//     experimentClassesOptions: {
//       immediate: true,
//       handler(newVal) {
//         if (newVal) {
//           this.selectedExperimentPluginId = Object.keys(newVal)[0];
//         }
//       },
//     },
//   },
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
        experimentId: this.selectedExperimentPluginId,
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
