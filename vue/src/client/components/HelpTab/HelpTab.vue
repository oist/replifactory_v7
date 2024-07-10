<template>
      <iframe
        id="helpIframe"
        :src="docUrl"
        class="h-100 w-100"
      ></iframe>
</template>

<script setup>
import { ref } from "vue";
const docUrl = ref("/help/index.html");
</script>

<style scoped></style>
