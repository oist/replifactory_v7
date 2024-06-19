<template>
  <CButtonGroup
    class="valve-buttons"
    :vertical="vertical"
    size="sm"
    role="group"
    aria-label="Valve control buttons"
  >
    <CButton
      v-c-tooltip="{ content: 'Close', placement: 'top' }"
      color="danger"
      :class="closeButtonClasses"
      :disabled="disabled"
      variant="outline"
      @click="close"
    >
      <CIcon icon="cilX" size="xl" />
    </CButton>
    <CButton
      v-c-tooltip="{ content: 'Beetween', placement: 'top' }"
      color="warning"
      :class="
        ['BEETWEEN', 'OPENING', 'CLOSING'].includes(state) ? 'active' : ''
      "
      :disabled="disabled"
      variant="outline"
    >
      <CIcon icon="cilLoopCircular" size="xl" />
    </CButton>
    <CButton
      v-c-tooltip="{ content: 'Open', placement: 'top' }"
      color="success"
      :class="openButtonClasses"
      :disabled="disabled"
      variant="outline"
      @click="open"
    >
      <CIcon icon="cilCheckAlt" size="xl" />
    </CButton>
  </CButtonGroup>
</template>

<script>
import { mapGetters } from "vuex";
import { CButton, CButtonGroup } from "@coreui/vue";
import { CIcon } from "@coreui/icons-vue";

export default {
  name: "ValveControl",
  components: {
    CButton,
    CButtonGroup,
    CIcon,
  },
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
    vertical: {
      type: Boolean,
      default: false,
    },
    title: {
      type: String,
      default: "Valve",
    },
    deviceId: {
      type: String,
      required: true,
    },
    reactorId: {
      type: Number,
      required: true,
    },
  },
  computed: {
    closeButtonClasses() {
      let classes = "";
      if (this.vertical) {
        classes += "rounded-top-5";
      }
      if (this.state === "CLOSE") {
        classes += " active";
      }
      return classes;
    },
    openButtonClasses() {
      let classes = "";
      if (this.vertical) {
        classes += "rounded-bottom-5";
      }
      if (this.state === "OPEN") {
        classes += " active";
      }
      return classes;
    },
    data() {
      const device = this.getDeviceById(this.deviceId);
      return device;
    },
    stateText() {
      return this.data != null ? this.data.state_string : "Undefined";
    },
    state() {
      return this.data != null ? this.data.state_id : "UNDEFINED";
    },
    ...mapGetters("machine", ["getDeviceById"]),
  },
  methods: {
    toggle() {},
    test() {},
    async close() {
      await this.sendCommand("close_valve");
    },
    async open() {
      await this.sendCommand("open_valve");
    },
    async sendCommand(command) {
      this.loading = true;
      this.showAlert = false;
      this.$store
        .dispatch("machine/reactorCommand", {
          reactorId: this.reactorId,
          command: command,
        })
        .then((data) => {
          console.debug(data);
        })
        .catch((err) => {
          this.loading = false;
          this.error = err.response.data;
          this.showAlert = true;
        });
    },
  },
};
</script>

<style>
.valve-buttons .btn {
  opacity: 50%;
}

.valve-buttons .active {
  opacity: 100%;
}

.valve-buttons .btn:hover {
  opacity: 80%;
}

.valve-buttons .btn:active {
  opacity: 90%;
}

.valve-buttons .btn:disabled {
  background-color: gray;
  border-color: gray;
  color: white;
  cursor: default;
  opacity: 80%;
}
</style>
