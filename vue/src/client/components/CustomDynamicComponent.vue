<template>
  <component :is="loadComponent" v-if="url" />
</template>

<script setup>
import { defineProps, defineAsyncComponent } from "vue";
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
      template: `<p>There is no component</p>`,
    };
  }
  try {
    return defineAsyncComponent(async () => {
      return await externalComponent(props.url);
    });
  } catch (e) {
    console.error(`Error loading plugin ${props.url}: ${e}`);
    return {
      template: `<p>Error loading plugin ${props.url}: ${e}</p>`,
    };
  }
}
</script>
