<template>
  <div class="MachineState">
    <dl class="row">
      <dt>State</dt>
      <dd>{{ state_string }}</dd>
      <dt>Queue</dt>
      <dd>
        Send: {{ sendQueue.size ? sendQueue.size : "0" }}<br />
        Commands: {{ commandQueue.size ? commandQueue.size : "0" }}
      </dd>
    </dl>
    <CButton
      type="button"
      color="danger"
      :disabled="!deviceControlEnabled"
      @click="handleCleanCommandQueueClick"
    >
      <CIcon :icon="icon.cilXCircle" size="xl" /> Abort
    </CButton>
  </div>
</template>

<script>
import { mapState, mapGetters } from "vuex";
import { CButton } from "@coreui/vue";
import { CIcon } from "@coreui/icons-vue";
import * as icon from "@coreui/icons";

export default {
  components: {
    CButton,
    CIcon,
  },
  setup() {
    return {
      icon,
    };
  },
  computed: {
    ...mapState("machine", {
      state_string: (state) => state.data.state.text,
      sendQueue: (state) => state.queue.send,
      commandQueue: (state) => state.queue.command,
    }),
    ...mapGetters("machine", {
      deviceControlEnabled: "isManualControlEnabled",
    }),
  },
  methods: {
    handleCleanCommandQueueClick() {
      this.$store
        .dispatch("machine/runCommand", {
          device: "command_queue",
          command: "clear",
        })
        .then((data) => {
          console.debug(data);
        })
        .catch((err) => {
          this.$store.dispatch("notifyWarning", {
            content: err.response.data,
          });
        });
    },
  },
};
</script>

<style scoped></style>
