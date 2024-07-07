<script setup>
import { ref, onBeforeMount } from "vue";
import { useStore } from "vuex";

const store = useStore();

const componentLoaded = ref(false);
const errorMessage = ref(null);

// Load plugins meta when component is created
onBeforeMount(() => {
  store.dispatch("plugins/fetchPluginsMeta")
  .then(() => {
    componentLoaded.value = true;
  })
  .catch((error) => {
    errorMessage.value = error;
  });
});
</script>

<template>
  <section v-if="!componentLoaded">
    <div v-if="errorMessage">
      <h1>Loading plugins failed</h1>
      <div v-html="errorMessage"></div>
    </div>
    <p v-else>Loading plugins...</p>
  </section>
  <router-view v-else />
</template>
