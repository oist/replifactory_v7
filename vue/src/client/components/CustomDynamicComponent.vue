<template>
  <div class="external-component-container">
    <component :is="AsyncComp" v-if="url"/>
  </div>
</template>

<script setup>
import { defineProps, watchEffect, ref, defineAsyncComponent } from "vue";
import { externalComponent } from "@/plugins.js";

const props = defineProps({
  url: {
    type: String,
    default: "",
  },
});
async function loadComponent() {
  if (!props.url) {
    return {
      template: `<p>URL is not provided</p>`,
    };
  }
  try {
    return await externalComponent(props.url);
  } catch (error) {
    console.error(error);
    return {
        template: `<p>${error.message}</p>`,
    };
  }
}

const AsyncComp = ref(null);
watchEffect(async () => {
  AsyncComp.value = defineAsyncComponent({
    loader: loadComponent,
    loadingComponent: {
      template: `<p>Loading...</p>`,
    },
    delay: 2000,
    timeout: 3000,
  });
});
// const AsyncComp = computed(() => defineAsyncComponent({
//   loader: loadComponent,
//   loadingComponent: {
//     template: `<p>Loading...</p>`,
//   },
//   delay: 2000,
//   timeout: 3000,
// }));
</script>
