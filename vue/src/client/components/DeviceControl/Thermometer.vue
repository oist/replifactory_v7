<template>
  <CCard style="width: 14rem" class="m-2 thermometer-control">
    <CCardBody>
      <CCardTitle>Thermometer</CCardTitle>
      <CCardSubtitle class="mb-2 text-muted">
        {{ label }}
      </CCardSubtitle>
      <CInputGroup class="mb-3">
        <CButton
          type="button"
          color="success"
          variant="outline"
          :class="state == 'WORKING' ? 'active' : ''"
          :disabled="disabled"
          @click="handleRefreshClick"
        >
          <CIcon icon="cilLoopCircular" size="xl" />
        </CButton>
        <CFormInput
          :id="deviceId + '-value'"
          v-model="value"
          placeholder="?"
          :aria-label="label + ' themperature'"
          :aria-describedby="deviceId + '-inputLabel'"
          readonly
        />
        <CInputGroupText :id="deviceId + '-inputLabel'">
          &deg;C
        </CInputGroupText>
      </CInputGroup>
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
  CInputGroupText,
  CCardTitle,
  CCardSubtitle,
} from "@coreui/vue";
import { CIcon } from "@coreui/icons-vue";
// import { cilLoopCircular } from "@coreui/icons";
import { mapGetters, mapState } from "vuex";

export default {
  name: "ThermometerControl",
  components: {
    CCard,
    CCardBody,
    CButton,
    CFormInput,
    CIcon,
    CInputGroup,
    CInputGroupText,
    CCardTitle,
    CCardSubtitle,
  },
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
    label: {
      type: String,
      default: "Thermometer",
    },
    deviceId: {
      type: String,
      required: true,
    },
  },
  setup() {
    return {
      // icon: {
      //   cilLoopCircular,
      // },
    };
  },
  computed: {
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
    value() {
      return this.data != null ? parseFloat(this.data.value).toFixed(2) : "?";
    },
    ...mapGetters("machine", ["getDeviceById"]),
    ...mapState(["debug"]),
  },
  methods: {
    handleRefreshClick() {
      this.$store
        .dispatch("machine/deviceCommand", {
          deviceId: this.deviceId,
          command: "measure",
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
/* .pump-control .btn {
    opacity: 50%;
}
.pump-control .btn:hover {
    opacity: 80%;
}
.pump-control .btn.active {
    opacity: 100%;
}
.pump-control .btn.active:hover {
    opacity: 80%;
}
.pump-control .btn:disabled {
    background-color: gray;
    border-color: gray;
    color: white;
    cursor: default;
    opacity: 80%;
} */
</style>
