<template>
  <CInputGroup class="mb-3 buttons-group">
    <CButton
      type="button"
      color="success"
      variant="outline"
      :class="state == 'WORKING' ? 'active' : ''"
      :disabled="disabled"
      @click="handlePumpButtonClick"
    >
      <CIcon icon="cilMediaPlay" size="xl" />
    </CButton>
    <CFormInput
      :id="deviceId + '-volume'"
      v-model="inputVolume"
      placeholder="&infin;"
      aria-label="Volume"
      :aria-describedby="deviceId + '-inputVolumeText'"
      :disabled="disabled"
    />
    <CInputGroupText :id="deviceId + '-inputVolumeText'"> ml </CInputGroupText>
    <CFormInput
      v-if="debug"
      :id="deviceId + '-speed'"
      v-model="inputSpeed"
      :placeholder="data.max_speed_rps"
      aria-label="Speed"
      :aria-describedby="deviceId + '-inputSpeedText'"
      :disabled="disabled"
    />
    <CInputGroupText v-if="debug" :id="deviceId + '-inputSpeedText'">
      rps
    </CInputGroupText>
  </CInputGroup>
</template>

<script>
import { CInputGroup, CButton, CFormInput, CInputGroupText } from "@coreui/vue";
import { CIcon } from "@coreui/icons-vue";
import { mapGetters, mapState } from "vuex";

export default {
  name: "PumpControl",
  components: {
    CButton,
    CFormInput,
    CIcon,
    CInputGroup,
    CInputGroupText,
  },
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
    label: {
      type: String,
      default: "Valve",
    },
    deviceId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      inputVolume: "",
      inputSpeed: "",
      motor: {
        profile: {
          acceleration: 0.0,
          deceleration: 0.0,
          max_speed_rps: 0,
          min_speed_rps: 0,
          full_step_speed: 0,
          kval_hold: 0,
          kval_run: 0,
          kval_acc: 0,
          kval_dec: 0,
          intersect_speed: 0,
          start_slope: 0,
          acceleration_final_slope: 0,
          deceleration_final_slope: 0,
          thermal_compensation_factor: 0,
          overcurrent_threshold: 0,
          stall_threshold: 0,
          step_mode: 0,
          alarm_enable: 0,
          clockwise: false,
        },
      },
      motorProfileVisisble: false,
    };
  },
  computed: {
    data() {
      const device = this.getDeviceById(this.deviceId);
      return device;
    },
    motor_profile() {
      let profile_proxy;
      if (
        this.data != null &&
        this.data.motor != null &&
        this.data.motor.profile != null
      ) {
        profile_proxy = this.data.motor.profile;
      } else {
        profile_proxy = this.motor.profile;
      }
      return {
        acceleration: parseFloat(profile_proxy["acceleration"]),
        deceleration: parseFloat(profile_proxy["deceleration"]),
        max_speed_rps: parseFloat(profile_proxy["max_speed_rps"]),
        min_speed_rps: parseFloat(profile_proxy["min_speed_rps"]),
        full_step_speed: parseInt(profile_proxy["full_step_speed"]),
        kval_hold: parseInt(profile_proxy["kval_hold"]),
        kval_run: parseInt(profile_proxy["kval_run"]),
        kval_acc: parseInt(profile_proxy["kval_acc"]),
        kval_dec: parseInt(profile_proxy["kval_dec"]),
        intersect_speed: parseInt(profile_proxy["intersect_speed"]),
        start_slope: parseInt(profile_proxy["start_slope"]),
        acceleration_final_slope: parseInt(
          profile_proxy["acceleration_final_slope"],
        ),
        deceleration_final_slope: parseInt(
          profile_proxy["deceleration_final_slope"],
        ),
        thermal_compensation_factor: parseInt(
          profile_proxy["thermal_compensation_factor"],
        ),
        overcurrent_threshold: parseInt(profile_proxy["overcurrent_threshold"]),
        stall_threshold: parseInt(profile_proxy["stall_threshold"]),
        step_mode: parseInt(profile_proxy["step_mode"]),
        alarm_enable: parseInt(profile_proxy["alarm_enable"]),
        clockwise:
          typeof profile_proxy["clockwise"] === "string"
            ? profile_proxy["clockwise"].toLowerCase() == "true"
            : profile_proxy["clockwise"],
      };
    },
    stateText() {
      return this.data != null ? this.data.state_string : "Undefined";
    },
    state() {
      return this.data != null ? this.data.state_id : "UNDEFINED";
    },
    ...mapGetters("machine", ["getDeviceById"]),
    ...mapState(["debug"]),
  },
  watch: {
    motor_profile(newVal) {
      this.motor.profile = newVal;
    },
  },
  methods: {
    convetAccelerationToFloat() {
      this.motor.profile.acceleration = parseFloat(
        this.motor.profile.acceleration,
      );
    },
    convertDecelerationToFloat() {
      this.motor.profile.deceleration = parseFloat(
        this.motor.profile.deceleration,
      );
    },
    convetMaxSpeedRPSToFloat() {
      this.motor.profile.max_speed_rps = parseFloat(
        this.motor.profile.max_speed_rps,
      );
    },
    convetMinSpeedRPSToFloat() {
      this.motor.profile.min_speed_rps = parseFloat(
        this.motor.profile.min_speed_rps,
      );
    },
    handleReloadButtonClick() {
      this.$store
        .dispatch("machine/deviceCommand", {
          command: "read_state",
          deviceId: this.deviceId,
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
    handlePumpButtonClick() {
      let pumpData = {
        command: "run",
        deviceId: this.deviceId,
      };
      if (this.inputVolume) {
        pumpData.volume = parseFloat(this.inputVolume);
        pumpData.command = "pump";
      }
      if (this.inputSpeed) {
        pumpData.rot_per_sec = parseFloat(this.inputSpeed);
      }
      this.$store
        .dispatch("machine/deviceCommand", pumpData)
        .then((data) => {
          console.debug(data);
        })
        .catch((err) => {
          this.$store.dispatch("notifyWarning", {
            content: err.response.data,
          });
        });
    },
    handleStopButtonClick() {
      this.$store
        .dispatch("machine/machineCommand", {
          command: "stop_pump",
          device_id: this.deviceId,
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
    handleSetProfileButtonClick() {
      this.$store
        .dispatch("machine/deviceCommand", {
          command: "set_profile",
          deviceId: this.deviceId,
          profile: this.motor_profile,
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

<style>
.pump-control .buttons-group .btn {
  opacity: 50%;
}

.pump-control .buttons-group .btn:hover {
  opacity: 80%;
}

.pump-control .buttons-group .btn.active {
  opacity: 100%;
}

.pump-control .buttons-group .btn.active:hover {
  opacity: 80%;
}

.pump-control .btn:disabled {
  background-color: gray;
  border-color: gray;
  color: white;
  cursor: default;
  opacity: 80%;
}
</style>
