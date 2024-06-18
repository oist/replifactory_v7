<template>
  <div>
    <CFormRange
      v-model.number="value"
      :min="min"
      :max="max"
      :step="step"
      :disabled="disabled"
      @input="handleChange"
    />
    <span>{{ value }}</span>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { CFormRange } from "@coreui/vue";

export default {
  name: "StirrerControl",
  components: {
    CFormRange,
  },
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
    deviceId: {
      type: String,
      required: true,
    },
    reactorId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      // value: 0,
      min: 0,
      max: 100,
      step: 1,
    };
  },
  computed: {
    data() {
      const device = this.getDeviceById(this.deviceId);
      return device;
    },
    value() {
      return (this.data.speed * 100) | 0;
    },
    ...mapGetters("machine", ["getDeviceById"]),
  },
  methods: {
    handleChange(event) {
      console.debug(event);
      this.$store
        .dispatch("machine/reactorCommand", {
          reactorId: this.reactorId,
          command: "stirrer",
          speed_ratio: parseFloat(event.target.value) / 100,
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
