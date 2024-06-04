<template>
    <CButtonGroup
      class="laser-buttons"
      :vertical="vertical"
      size="sm"
      role="group"
      aria-label="Laser control buttons"
    >
      <CButton
        v-c-tooltip="{ content: 'Off', placement: 'top' }"
        color="danger"
        :class="offButtonClasses"
        :disabled="disabled"
        variant="outline"
        @click="switch_off"
      >
        <CIcon :icon="icon.cilLightbulb" size="xl" />
      </CButton>
      <CButton
        v-c-tooltip="{ content: 'On', placement: 'top' }"
        color="success"
        :class="onButtonClasses"
        :disabled="disabled"
        variant="outline"
        @click="switch_on"
      >
        <CIcon :icon="icon.cilLightbulb" size="xl" />
      </CButton>
    </CButtonGroup>
</template>

<script>
import { mapGetters } from "vuex";
import { CButton, CButtonGroup } from "@coreui/vue";
import { CIcon } from "@coreui/icons-vue";
import * as icon from "@coreui/icons";

export default {
  name: "LaserControl",
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
      default: "Laser",
    },
    deviceId: {
      type: String,
      required: true,
    },
  },
  setup() {
    return {
      icon,
    };
  },
  computed: {
    offButtonClasses() {
      let classes = "";
      if (this.vertical) {
        classes += "rounded-top-5";
      }
      if (this.state === "OFF") {
        classes += " active";
      }
      return classes;
    },
    onButtonClasses() {
      let classes = "";
      if (this.vertical) {
        classes += "rounded-bottom-5";
      }
      if (this.state === "ON") {
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
    async switch_off() {
      await this.sendCommand("off");
    },
    async switch_on() {
      await this.sendCommand("on");
    },
    async sendCommand(command) {
      this.loading = true;
      this.showAlert = false;
      this.$store
        .dispatch("machine/runCommand", {
          device: "laser",
          command: command,
          deviceId: this.deviceId,
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
.laser-buttons .btn {
  opacity: 50%;
}

.laser-buttons .active {
  opacity: 100%;
}

.laser-buttons .btn:hover {
  opacity: 80%;
}

.laser-buttons .btn:active {
  opacity: 90%;
}

.laser-buttons .btn:disabled {
  background-color: gray;
  border-color: gray;
  color: white;
  cursor: default;
  opacity: 80%;
}
</style>
