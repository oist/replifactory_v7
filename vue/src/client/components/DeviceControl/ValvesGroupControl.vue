<template>
  <Valve
    v-for="i in 7"
    :key="i"
    class="mx-4 my-1"
    :device-id="'valve-' + (i - 1)"
    :title="'Valve ' + i"
    :disabled="disabled"
  />
</template>

<script>
import Valve from "./Valve";

export default {
  name: "ValvesGroupControl",
  components: {
    Valve,
  },
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
  },
};
</script>

<style></style>
