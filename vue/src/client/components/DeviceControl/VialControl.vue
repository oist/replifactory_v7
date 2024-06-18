<template>
  <div
    class="progress progress-bar-vertical update-button"
    :class="disabled ? 'disabled' : ''"
    @click="updateOpticalDensity"
  >
    <div
      class="progress-bar"
      role="progressbar"
      aria-valuenow="30"
      aria-valuemin="0"
      aria-valuemax="100"
      style="height: 30%"
    >
      <span class="sr-only">OD: {{ od }}</span>
      <span v-if="debug" class="sr-only">BG: {{ background }}</span>
      <span v-if="debug" class="sr-only">TR: {{ transmitted }}</span>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapState } from "vuex";
export default {
  name: "ValvesGroupControl",
  components: {},
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
    width: {
      type: String,
      default: "75px",
    },
    height: {
      type: String,
      default: "160px",
    },
    odSensorId: {
      type: String,
      default: null,
    },
    reactorId: {
      type: String,
      required: true,
    },
  },
  computed: {
    data() {
      const device = this.getDeviceById(this.odSensorId);
      return device;
    },
    ...mapGetters("machine", ["getDeviceById"]),
    ...mapState(["debug"]),
    od() {
      const value = this.data.value;
      if (value != null) {
        return value.toPrecision(3);
      } else {
        return "N/A";
      }
    },
    background() {
      const value = this.data.background;
      if (value != null) {
        return value.toPrecision(3);
      } else {
        return "N/A";
      }
    },
    transmitted() {
      const value = this.data.transmitted;
      if (value != null) {
        return value.toPrecision(3);
      } else {
        return "N/A";
      }
    },
  },
  methods: {
    updateOpticalDensity(event) {
      console.debug(event);
      this.$store
        .dispatch("machine/reactorCommand", {
          reactorId: this.reactorId,
          command: "measure_od",
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
.update-button {
  cursor: pointer;
}
.update-button:hover {
  /* background-color: lightgray; */
  opacity: 80%;
}
.update-button:active {
  opacity: 90%;
}
.update-button.disabled .update-button.disabled .progress-bar {
  background-color: gray;
  border-color: gray;
  color: white;
  cursor: default;
  opacity: 80%;
}

.progress-bar-vertical {
  width: 100%;
  min-height: 12rem;
  display: flex;
  align-items: flex-end;
  margin-right: 20px;
  float: left;
}

.progress-bar-vertical .progress-bar {
  width: 100%;
  height: 0;
  -webkit-transition: height 0.6s ease;
  -o-transition: height 0.6s ease;
  transition: height 0.6s ease;
}
</style>
