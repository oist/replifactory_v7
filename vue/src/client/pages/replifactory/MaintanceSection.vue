<template>
  <div class="external-component-container">
    <AsyncComp />
  </div>
</template>

<script setup>
import { defineAsyncComponent } from "vue";
import { externalComponent } from "@/plugins.js";

const AsyncComp = defineAsyncComponent({
//   externalComponent(`/static/build/external-component/vue3-other-part.umd.js`),
    loader: () => externalComponent("/plugins/flask_app.replifactory.plugins.experiments.od_measure.plugin.ODMeasureExperimentPlugin/od-measure-replyfactory-plugin.dad92d61dce13c7e.umd.min.js"),
    // loader: () => externalComponent("/plugins/flask_app.replifactory.plugins.experiments.od_measure.plugin.EndlessGrowthExperimentPlugin/replifactory_endless_growth_plugin.umd.cjs"),
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
