<template>
  <div class="container d-flex align-items-stretch">
    <div class="row align-items-stretch flex-fill bg-body">
        <div class="col-md-3 p-3 border-end">
            <h4>Connection</h4>
            <MachineConnection />
            <h4 class="mt-3">Machine State</h4>
            <MachineState />
        </div>
        <div class="col-md-9 p-3">
            <h4>Running experiments</h4>
            <ExperimentsStatuses />
        </div>
    </div>
  </div>
</template>

<script>
import MachineConnection from "@/client/components/machine/MachineConnection.vue";
import MachineState from "@/client/components/machine/MachineState.vue";
import ExperimentsStatuses from "@/client/components/experiment/ExperimentsStatuses.vue";
export default {
  components: {
    MachineConnection,
    MachineState,
    ExperimentsStatuses,
  },
};
</script>
