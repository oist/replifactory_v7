<template>
  <div class="container">
    <MachineConnection />
    <MachineState />
  </div>
</template>

<script>
import MachineConnection from "@/client/components/machine/MachineConnection.vue";
import MachineState from "@/client/components/machine/MachineState.vue";
export default {
  components: {
    MachineConnection,
    MachineState,
  },
};
</script>
