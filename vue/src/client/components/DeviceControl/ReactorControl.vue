<template>
  <CCard style="width: 11rem" class="m-2">
    <CCardBody>
      <CCardTitle>{{ reactor.title }}</CCardTitle>
      <CCardSubtitle class="mb-2 text-muted">
        {{ reactor.subtitle }}
      </CCardSubtitle>
      <!-- <CCardText>
                Some quick example text to build on the card title and make up the bulk of the card's content.
            </CCardText> -->
      <!-- <PumpControl :disabled="!deviceControlEnabled" /> -->
      <Valve
        :key="valve.id"
        :reactor-id="reactor.id"
        class="my-1"
        :device-id="valve.id"
        :title="valve.title"
        :disabled="disabled"
      />
      <VialControl
        :od-sensor-id="odSensor.id"
        :reactor-id="reactor.id"
        :disabled="disabled"
        class="my-2 mx-0"
        height="100px"
      />
      <!-- <ValvesGroupControl :disabled="!deviceControlEnabled" /> -->
      <!-- <ValveControl :disabled="!deviceControlEnabled" /> -->
      <!-- <StirrerControl :disabled="!deviceControlEnabled" /> -->
      <!-- <ODControl :disabled="!deviceControlEnabled" /> -->
      <!-- <RangeSlider></RangeSlider> -->
      <LaserControl
        :key="laser.id"
        :reactor-id="reactor.id"
        :device-id="laser.id"
        :title="laser.title"
        :disabled="disabled"
      />
      <Stirrer
        :key="stirrer.id"
        :reactor-id="reactor.id"
        :device-id="stirrer.id"
        :title="stirrer.title"
        :disabled="disabled"
      />
    </CCardBody>
  </CCard>
</template>

<script>
// import PumpControl from './PumpControl';
// import ValvesGroupControl from './ValvesGroupControl';
// import ValveControl from './ValveControl';
// import StirrerControl from './StirrerControl';
// import ODControl from './ODControl';
import VialControl from "./VialControl.vue";
import Valve from "./Valve.vue";
import LaserControl from "./LaserControl.vue";
import Stirrer from "./Stirrer.vue";
// import RangeSlider from '@/client/components/widgets/RangeSlider';
import { CCard, CCardBody, CCardTitle, CCardSubtitle } from "@coreui/vue";

export default {
  components: {
    // PumpControl,
    // ValvesGroupControl,
    // ValveControl,
    // StirrerControl,
    // ODControl,
    VialControl,
    Valve,
    LaserControl,
    Stirrer,
    // RangeSlider,
    // CFormSwitch,
    CCard,
    CCardBody,
    CCardTitle,
    CCardSubtitle,
    // CCardText,
  },
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
    id: {
      type: Number,
      default: 0,
    },
    title: {
      type: String,
      default: null,
    },
    subtitle: {
      type: String,
      default: null,
    },
    valveId: {
      type: String,
      default: null,
    },
    valveTitle: {
      type: String,
      default: null,
    },
    laserId: {
      type: String,
      default: null,
    },
    laserTitle: {
      type: String,
      default: null,
    },
    stirrerId: {
      type: String,
      default: null,
    },
    stirrerTitle: {
      type: String,
      default: null,
    },
    odSensorId: {
      type: String,
      default: null,
    },
    odSensorTitle: {
      type: String,
      default: null,
    },
  },
  computed: {
    reactor() {
      return {
        id: this.id,
        title: this.title != null ? this.title : `Reactor ${this.id}`,
        subtitle:
          this.subtitle != null ? this.subtitle : `Lactobacillus plantarum`,
      };
    },
    valve() {
      return {
        id: this.valveId != null ? this.valveId : `valve-${this.id}`,
        title: this.valveTitle != null ? this.valveTitle : `Valve ${this.id}`,
      };
    },
    laser() {
      return {
        id: this.laserId != null ? this.laserId : `laser-${this.id}`,
        title: this.laserTitle != null ? this.laserTitle : `Laser ${this.id}`,
      };
    },
    stirrer() {
      return {
        id: this.stirrerId != null ? this.stirrerId : `stirrer-${this.id}`,
        title:
          this.stirrerTitle != null ? this.stirrerTitle : `Stirrer ${this.id}`,
      };
    },
    odSensor() {
      return {
        id:
          this.odSensorId != null
            ? this.odSensorId
            : `optical-density-sensor-${this.id}`,
        title:
          this.odSensorTitle != null
            ? this.odSensorTitle
            : `Optical Density Sensor ${this.id}`,
      };
    },
  },
};
</script>

<style></style>
