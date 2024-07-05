<template>
  <div class="external-component-container">
    <!-- <div v-if="loadError" class="error-message">{{ loadError }}</div>
    <component :is="AsyncComp" v-else /> -->
    <component :is="AsyncComp" />
  </div>
</template>

<script setup>
import { defineAsyncComponent } from "vue";
import { externalComponent } from "@/plugins.js";

// const loadError = ref(""); // Reactive property to store the error message
// const isLoading = ref(true); // Track loading state

// Custom loader function with error handling
// async function loadComponent() {
//   try {
//     const component = await externalComponent(
//     //   "/static/build/external-component/vue3-other-part.umd.js",
//     //   "/plugins/flask_app.replifactory.plugins.experiments.od_measure.plugin.ODMeasureExperimentPlugin/od-measure-replyfactory-plugin.dad92d61dce13c7e.umd.min.js"
//       "/plugins/flask_app.replifactory.plugins.experiments.endless_growth.plugin.EndlessGrowthExperimentPlugin/replifactory_endless_growth_plugin.umd.cjs",
//     );
//     isLoading.value = false; // Update loading state
//     return component;
//   } catch (error) {
//     isLoading.value = false; // Update loading state
//     loadError.value = "Failed to load component: " + error.message; // Set the error message
//     // throw error; // Rethrow the error if you need further error handling
//     return {
//         template: `<p>Error loading plugin: ${error.message}</p>`,
//     };
//   }
// }

// const AsyncComp = defineAsyncComponent({
//   loader: loadComponent,
//   loadingComponent: {
//     template: `<p>Loading...</p>`,
//   },
//   delay: 2000,
//   timeout: 3000,
// });
const AsyncComp = defineAsyncComponent({
    // loader: () =>  externalComponent(`/static/build/external-component/vue3-other-part.umd.js`),
    // loader: () => externalComponent(`/static/build/external-component/sd-components.umd.js`),
    loader: () => externalComponent("/plugins/flask_app.replifactory.plugins.experiments.od_measure.plugin.ODMeasureExperimentPlugin/od-measure-replyfactory-plugin.umd.min.js"),
    // loader: () => externalComponent("/plugins/flask_app.replifactory.plugins.experiments.endless_growth.plugin.EndlessGrowthExperimentPlugin/replifactory_endless_growth_plugin.umd.cjs"),
    loadingComponent: {
        template: `<p>Loading...</p>`,
    },
    delay: 2000,
    errorComponent: {
        template: `<p>Error loading plugin</p>`,
    },
    timeout: 3000,
});
</script>
