<template>
  <component :is="loadComponent" v-if="url" />
</template>

<script setup>
import { defineProps, defineAsyncComponent } from 'vue'; // Import defineAsyncComponent from the Vue Composition API

const props = defineProps({
  url: {
    type: String,
    default: "",
  },
});
async function loadPlugin(url) {
  //   try {
  // Assuming moduleInfo.url contains the URL to the module
  const module = await import(/* @vite-ignore */ url);
  // if (typeof module.default === "function") {
  //     // Pass the Vue app instance to the imported module if it exports a function
  //     module.default(app);
  // } else {
  //     // Use the module directly if it's not a function (e.g., a Vue plugin)
  //     app.use(module.default);
  // }
  return module;
  //   } catch (e) {
  //     console.error(`Error loading plugin ${url}: ${e}`);
  //   }
}
async function loadComponent() {
  if (!props.url) {
    return {
      template: `<p>There is no component</p>`,
    };
  }
  try {
    return defineAsyncComponent(async () => {
        return await loadPlugin(props.url);
    });
    // return await loadPlugin(props.url);
  } catch (e) {
    console.error(`Error loading plugin ${props.url}: ${e}`);
    return {
      template: `<p>Error loading plugin ${props.url}: ${e}</p>`,
    };
  }
  //   return app.component("DynamicComponent");
}
</script>
