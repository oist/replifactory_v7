<template>
  <div
    class="DeviceControl container-fluid"
    :class="{ 'device-disconnected': deviceConnected === false }"
  >
    <!-- <div class="disconnected-overlay" v-if="deviceConnected === false"></div> -->
    <!-- <div class="centered-text" v-if="deviceConnected === false"> device connection not available </div> -->
    <!-- <div class="experiment-running-overlay" v-if="deviceControlEnabled === false"></div> -->
    <!-- <div style="text-align: right;">
      <CFormSwitch label="Calibration Mode" id="formSwitchCheckChecked" v-model="calibrationModeEnabled"
        @change="toggleCalibrationMode" />
    </div> -->

    <!-- <PumpControl :disabled="!deviceControlEnabled" /> -->
    <CRow>
      <ReactorControl
        v-for="i in 7"
        :id="i"
        :key="i"
        :disabled="!deviceControlEnabled"
      />
    </CRow>
    <CRow v-if="debug">
      <Pump
        :disabled="!deviceControlEnabled"
        device-id="pump-1"
        label="[1] Main pump"
      />
      <Pump
        :disabled="!deviceControlEnabled"
        device-id="pump-2"
        label="[2] Drug pump"
      />
      <Pump
        :disabled="!deviceControlEnabled"
        device-id="pump-4"
        label="[4] Waste pump"
      />
    </CRow>
    <CRow>
      <Thermometer
        :disabled="!deviceControlEnabled"
        device-id="thermometer-0x48"
        label="Main board"
      />
      <Thermometer
        :disabled="!deviceControlEnabled"
        device-id="thermometer-0x49"
        label="Reactor 1"
      />
      <Thermometer
        :disabled="!deviceControlEnabled"
        device-id="thermometer-0x4a"
        label="Reactor 7"
      />
    </CRow>
    <!-- <ValvesGroupControl :disabled="!deviceControlEnabled" /> -->
    <!-- <ValveControl :disabled="!deviceControlEnabled" /> -->
    <!-- <StirrerControl :disabled="!deviceControlEnabled" /> -->
    <!-- <ODControl :disabled="!deviceControlEnabled" /> -->
  </div>
</template>

<script>
// import PumpControl from './PumpControl';
// import ValvesGroupControl from './ValvesGroupControl';
// import ValveControl from './ValveControl';
// import StirrerControl from './StirrerControl';
// import ODControl from './ODControl';
// import VialControl from './VialControl';
import ReactorControl from "./ReactorControl.vue";
import Pump from "./Pump.vue";
import Thermometer from "./Thermometer.vue";
import { mapState, mapGetters, mapMutations, mapActions } from "vuex";
import { CRow } from "@coreui/vue";

export default {
  components: {
    // PumpControl,
    // ValvesGroupControl,
    // ValveControl,
    // StirrerControl,
    // ODControl,
    // VialControl,
    ReactorControl,
    Pump,
    Thermometer,
    CRow,
    // CFormSwitch,
  },
  data() {
    return {
      controlsVisible: false,
    };
  },
  computed: {
    ...mapState("device", [
      "calibrationModeEnabled",
      "stirrers",
      "pumps",
      "valves",
      "ods",
    ]),
    ...mapState(["debug"]),
    ...mapGetters("machine", {
      deviceConnected: "isConnected",
      deviceControlEnabled: "isManualControlEnabled",
    }),
  },
  // watch: {
  //   deviceControlEnabled(newVal) {
  //     if (newVal) {
  //       this.controlsVisible = true;
  //     } else {
  //       this.controlsVisible = false;
  //     }
  //   },
  // },
  mounted() {
    // if not connected, try to connect
    // if (!this.deviceConnected) {
    //   this.connectDevice().then(() => {
    //     this.getAllDeviceData().then(() => {
    //     });
    //   });
    // }
  },
  methods: {
    ...mapMutations("device", [
      "toggleCalibrationMode",
      "setDeviceControlEnabled",
    ]),
    ...mapActions("device", ["getAllDeviceData"]),
    ...mapActions(["connectDevice"]),
  },
};
</script>

<style scoped>
.disconnected-overlay {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(128, 128, 128, 0.9);
  /* gray with 50% opacity */
  z-index: 1;
  /* to ensure the overlay is on top */
}

.experiment-running-overlay {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(250, 1, 59, 0.5);
  /* gray with 50% opacity */
  z-index: 1;
  /* to ensure the overlay is on top */
}

.centered-text {
  position: fixed;
  top: 50%;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  /*font-weight: bold;*/
  font-size: 3em;
  color: rgba(255, 255, 255, 0.5);
  z-index: 2;
  transform: translateY(-80%);
}

.device-disconnected {
  position: relative;
  /* this is needed to position the overlay correctly */
}
</style>
