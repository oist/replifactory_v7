<template>
  <CCard
    :style="debug ? 'width: 24rem' : 'width: 16rem'"
    class="m-2 pump-control"
  >
    <CCardBody>
      <CCardTitle>{{ label }} <span class="badge text-bg-light">{{ state }}</span></CCardTitle>

      <CInputGroup class="mb-3 buttons-group">
        <CButton
          type="button"
          color="danger"
          variant="outline"
          :class="state == 'OPERATIONAL' ? 'active' : ''"
          :disabled="disabled"
          @click="handleStopButtonClick"
        >
          <CIcon icon="cilXCircle" size="xl" />
        </CButton>
        <CButton
          type="button"
          color="success"
          variant="outline"
          :class="state == 'WORKING' ? 'active' : ''"
          :disabled="disabled"
          @click="handlePumpButtonClick"
        >
          <CIcon icon="cilShower" size="xl" />
        </CButton>
        <CFormInput
          :id="deviceId + '-volume'"
          v-model="inputVolume"
          placeholder="&infin;"
          aria-label="Volume"
          :aria-describedby="deviceId + '-inputVolumeText'"
          :disabled="disabled"
        />
        <CInputGroupText :id="deviceId + '-inputVolumeText'">
          ml
        </CInputGroupText>
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
      <CButton
        v-if="debug"
        color="primary"
        href="#"
        @click="motorProfileVisisble = !motorProfileVisisble"
      >
        {{ motorProfileVisisble ? "Hide profile" : "Show profile" }}
      </CButton>
      <CButton
        v-if="debug"
        color="primary"
        variant="outline"
        :disabled="disabled"
        class="ms-1"
        @click="handleReloadButtonClick"
      >
        <CIcon icon="cilReload" />
      </CButton>
      <CCollapse v-if="debug" :visible="motorProfileVisisble">
        <CCard class="mt-3">
          <CCardBody>
            <CInputGroup class="mb-1">
              <CInputGroupText :id="deviceId + '-profile-acceleration-text'">
                Acceleration (steps/sec²)
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-acceleration'"
                v-model.number="motor.profile.acceleration"
                type="number"
                min="14.55"
                max="59590"
                step="14.55"
                :aria-label="deviceId + ' acceleration'"
                :aria-describedby="deviceId + '-profile-acceleration-text'"
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText :id="deviceId + '-profile-deceleration-text'">
                Deceleration (steps/sec²)
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-deceleration'"
                v-model.number="motor.profile.deceleration"
                type="number"
                min="14.55"
                max="59590"
                step="14.55"
                :aria-label="deviceId + ' deceleration'"
                :aria-describedby="deviceId + '-profile-deceleration-text'"
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText :id="deviceId + '-profile-max_speed_rps-text'">
                Max Speed (rps)
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-max_speed_rps'"
                v-model.number="motor.profile.max_speed_rps"
                type="number"
                min="0.07625"
                max="78.05"
                step="0.07625"
                :aria-label="deviceId + ' max speed rps'"
                :aria-describedby="deviceId + '-profile-max_speed_rps-text'"
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText :id="deviceId + '-profile-min_speed_rps-text'">
                Min Speed (rps)
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-min_speed_rps'"
                v-model.number="motor.profile.min_speed_rps"
                type="number"
                min="0"
                max="4.8815"
                step="0.00119"
                :aria-label="deviceId + ' min speed rps'"
                :aria-describedby="deviceId + '-profile-min_speed_rps-text'"
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText :id="deviceId + '-profile-full_step_speed-text'">
                Full Step Speed (rps)
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-full_step_speed'"
                v-model.number="motor.profile.full_step_speed"
                type="number"
                min="0.03815"
                max="78.125"
                step="0.07625"
                :aria-label="deviceId + ' full step speed'"
                :aria-describedby="deviceId + '-profile-full_step_speed-text'"
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText :id="deviceId + '-profile-kval_hold-text'">
                Kval Hold (Vs x K)
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-kval_hold'"
                v-model.number="motor.profile.kval_hold"
                type="number"
                min="0"
                max="0.996"
                step="0.004"
                :aria-label="deviceId + ' kval hold'"
                :aria-describedby="deviceId + '-profile-kval_hold-text'"
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText :id="deviceId + '-profile-kval_run-text'">
                Kval Run (Vs x K)
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-kval_run'"
                v-model.number="motor.profile.kval_run"
                type="number"
                min="0"
                max="0.996"
                step="0.004"
                :aria-label="deviceId + ' kval run'"
                :aria-describedby="deviceId + '-profile-kval_run-text'"
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText :id="deviceId + '-profile-kval_acc-text'">
                Kval Acc (Vs x K)
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-kval_acc'"
                v-model.number="motor.profile.kval_acc"
                type="number"
                min="0"
                max="0.996"
                step="0.004"
                :aria-label="deviceId + ' kval acc'"
                :aria-describedby="deviceId + '-profile-kval_acc-text'"
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText :id="deviceId + '-profile-kval_dec-text'">
                Kval Dec (Vs x K)
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-kval_dec'"
                v-model.number="motor.profile.kval_dec"
                type="number"
                min="0"
                max="0.996"
                step="0.004"
                :aria-label="deviceId + ' kval dec'"
                :aria-describedby="deviceId + '-profile-kval_dec-text'"
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText :id="deviceId + '-profile-intersect_speed-text'">
                Intersect Speed (rps)
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-intersect_speed'"
                v-model.number="motor.profile.intersect_speed"
                type="number"
                min="0"
                max="4.8825"
                step="0.000298"
                :aria-label="deviceId + ' intersect speed'"
                :aria-describedby="deviceId + '-profile-intersect_speed-text'"
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText :id="deviceId + '-profile-start_slope-text'">
                Start Slope (sec/step)
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-start_slope'"
                v-model.number="motor.profile.start_slope"
                type="number"
                min="0"
                max="0.004"
                step="0.000015"
                :aria-label="deviceId + ' start slope'"
                :aria-describedby="deviceId + '-profile-start_slope-text'"
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText
                :id="deviceId + '-profile-acceleration_final_slope-text'"
              >
                Acc Final Slope (sec/step)
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-acceleration_final_slope'"
                v-model.number="motor.profile.acceleration_final_slope"
                type="number"
                min="0"
                max="0.004"
                step="0.000015"
                :aria-label="deviceId + ' acceleration final slope'"
                :aria-describedby="
                  deviceId + '-profile-acceleration_final_slope-text'
                "
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText
                :id="deviceId + '-profile-deceleration_final_slope-text'"
              >
                Dec Final Slope (sec/step)
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-deceleration_final_slope'"
                v-model.number="motor.profile.deceleration_final_slope"
                type="number"
                min="0"
                max="0.004"
                step="0.000015"
                :aria-label="deviceId + ' deceleration final slope'"
                :aria-describedby="
                  deviceId + '-profile-deceleration_final_slope-text'
                "
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText
                :id="deviceId + '-profile-thermal_compensation_factor-text'"
              >
                Thermal Compensation Factor
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-thermal_compensation_factor'"
                v-model.number="motor.profile.thermal_compensation_factor"
                type="number"
                min="1"
                max="1.46875"
                step="0.03125"
                :aria-label="deviceId + ' thermal compensation factor'"
                :aria-describedby="
                  deviceId + '-profile-thermal_compensation_factor-text'
                "
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText
                :id="deviceId + '-profile-overcurrent_threshold-text'"
              >
                Overcurrent Threshold (A)
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-overcurrent_threshold'"
                v-model.number="motor.profile.overcurrent_threshold"
                type="number"
                min="0.375"
                max="6"
                step="0.375"
                :aria-label="deviceId + ' overcurrent threshold'"
                :aria-describedby="
                  deviceId + '-profile-overcurrent_threshold-text'
                "
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText :id="deviceId + '-profile-stall_threshold-text'">
                Stall Threshold (A)
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-stall_threshold'"
                v-model.number="motor.profile.stall_threshold"
                type="number"
                min="0.3125"
                max="4"
                step="0.3125"
                :aria-label="deviceId + ' stall threshold'"
                :aria-describedby="deviceId + '-profile-stall_threshold-text'"
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText :id="deviceId + '-profile-step_mode-text'">
                Step Mode
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-step_mode'"
                v-model.number="motor.profile.step_mode"
                type="number"
                min="0"
                max="7"
                step="1"
                :aria-label="deviceId + ' step mode'"
                :aria-describedby="deviceId + '-profile-step_mode-text'"
                :disabled="disabled"
              />
            </CInputGroup>
            <CInputGroup class="mb-1">
              <CInputGroupText :id="deviceId + '-profile-alarm_enable-text'">
                Alarm Enable
              </CInputGroupText>
              <CFormInput
                :id="deviceId + '-profile-alarm_enable'"
                v-model.number="motor.profile.alarm_enable"
                :aria-label="deviceId + ' alarm enable'"
                :aria-describedby="deviceId + '-profile-alarm_enable-text'"
                :disabled="disabled"
              />
            </CInputGroup>
            <!-- <CInputGroup class="mb-1">
              <CInputGroupText :id="deviceId + '-profile-clockwise-text'">
                Clockwise
              </CInputGroupText> -->
              <CFormCheck
                :id="deviceId + '-profile-clockwise'"
                v-model="motor.profile.clockwise"
                :aria-label="deviceId + ' clockwise'"
                :aria-describedby="deviceId + '-profile-clockwise-text'"
                :disabled="disabled"
                label="Clockwise"
                :reverse="true"
              />
            <!-- </CInputGroup> -->
            <CButton
              type="button"
              color="success"
              :disabled="disabled"
              @click="handleSetProfileButtonClick"
            >
              Save
            </CButton>
          </CCardBody>
        </CCard>
      </CCollapse>
    </CCardBody>
  </CCard>
</template>

<script>
import {
  CCard,
  CCardBody,
  CInputGroup,
  CButton,
  CFormInput,
  CFormCheck,
  CInputGroupText,
  CCardTitle,
  CCollapse,
} from "@coreui/vue";
import { CIcon } from "@coreui/icons-vue";
import { mapGetters, mapState } from "vuex";

export default {
  name: "PumpControl",
  components: {
    CCard,
    CCardBody,
    CButton,
    CFormInput,
    CFormCheck,
    CIcon,
    CInputGroup,
    CInputGroupText,
    CCardTitle,
    CCollapse,
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
      let profile_proxy
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
          acceleration_final_slope: parseInt(profile_proxy["acceleration_final_slope"]),
          deceleration_final_slope: parseInt(profile_proxy["deceleration_final_slope"]),
          thermal_compensation_factor:
          parseInt(profile_proxy["thermal_compensation_factor"]),
          overcurrent_threshold: parseInt(profile_proxy["overcurrent_threshold"]),
          stall_threshold: parseInt(profile_proxy["stall_threshold"]),
          step_mode: parseInt(profile_proxy["step_mode"]),
          alarm_enable: parseInt(profile_proxy["alarm_enable"]),
          clockwise: typeof profile_proxy["clockwise"] === 'string'
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
      this.motor.profile.acceleration = parseFloat(this.motor.profile.acceleration);
    },
    convertDecelerationToFloat() {
      this.motor.profile.deceleration = parseFloat(this.motor.profile.deceleration);
    },
    convetMaxSpeedRPSToFloat() {
      this.motor.profile.max_speed_rps = parseFloat(this.motor.profile.max_speed_rps);
    },
    convetMinSpeedRPSToFloat() {
      this.motor.profile.min_speed_rps = parseFloat(this.motor.profile.min_speed_rps);
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
