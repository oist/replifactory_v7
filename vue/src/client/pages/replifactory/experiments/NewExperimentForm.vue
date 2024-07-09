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
        <component :is="parametersComponent" @update-parameters="handleUpdateParameters" />
        <!-- <CustomDynamicComponent :url="parametersComponent" /> -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeMount, watch } from "vue";
import { useStore } from "vuex";
import { CFormSelect, CInputGroup, CButton } from "@coreui/vue";
import { defineAsyncComponent } from "vue";
import { componentLoader } from "@/plugins.js";

const store = useStore();

const selectedExperimentPluginId = ref(undefined);
const experimentParameters = ref({});
const isExperimentRunning = ref(false);

const getExperimentsPlugins = computed(
  () => store.getters["plugins/getExperimentsPlugins"],
);
const getPlugin = (id) => store.getters["plugins/getPlugin"](id);

const modifiedExperimentClassesOptions = computed(() => {
  let options = {
    none: "Select an option...",
  };
  getExperimentsPlugins.value.forEach((plugin) => {
    options[plugin.id] = plugin.name;
  });
  return options;
});

const selectedExperiment = computed(() => {
  const plugin = getPlugin(selectedExperimentPluginId.value);
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
});
const descriptionComponent = computed(() => {
  return selectedExperiment.value.description;
});
const parametersComponent = computed(() => {
  return selectedExperiment.value.parameters;
});
const experimentTitle = computed(() => {
  return selectedExperiment.value
    ? selectedExperiment.value.title
    : "Untitiled Experiment";
});

watch(selectedExperimentPluginId, (newVal, oldVal) => {
  // Clean experimentParameters when selectedExperimentPluginId changes
  experimentParameters.value = {};
});

onBeforeMount(() => {
  getExperimentClassesOptions();
});

function handleUpdateParameters(params) {
  experimentParameters.value = params;
}

function getExperimentClassesOptions() {
  store.dispatch("experiment/getExperimentsClassesOptions").catch((err) => {
    store.dispatch("notifyWarning", {
      content: err.response.data,
    });
  });
}
function startExperiment() {
  sendExperimentCommand("start", experimentParameters.value);
}
function stopExperiment() {
  sendExperimentCommand("stop");
}
function pauseExperiment() {
  sendExperimentCommand("pause");
}
// function  resumeExperiment() {
//   sendExperimentCommand("resume");
// };
function sendExperimentCommand(command, args) {
  const data = {
    experimentId: selectedExperimentPluginId,
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
