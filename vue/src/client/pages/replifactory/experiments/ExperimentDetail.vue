<script setup>
import { shallowRef, markRaw, onBeforeMount, defineAsyncComponent } from "vue";
import { useStore } from "vuex";
import { useRoute } from "vue-router";
import { componentLoader } from "@/plugins.js";

const store = useStore();
const route = useRoute();

const dashboardComponent = shallowRef(markRaw({
    template: "<div>Loading dashboard...</div>",
}));

onBeforeMount(async () => {
    const experimentId = route.params.id;
    store.dispatch("experiment/getExperiment", experimentId)
    .then((experiment) => {
        const module = store.getters["plugins/getUiModuleForClass"](experiment.class, "dashboard");
        if (!module) {
            console.error("Dashboard component not found for the experiment");
            return;
        }
        dashboardComponent.value = defineAsyncComponent({
            loader: componentLoader(module.path),
        });
    }).catch((error) => {
        console.error(error);
    });
});
</script>

<template>
    <div class="container">
        <component :is="dashboardComponent" />
    </div>
</template>