<template>
    <CCard :style="debug ? 'width: 24rem' : 'width: 16rem'" class="m-2">
        <CCardBody>
            <CCardTitle>{{ label }}</CCardTitle>
            <CInputGroup class="mb-3">
                <CButton type="button" color="danger" @click="handleStopButtonClick" variant="outline"
                    :class="state == 'OPERATIONAL' ? 'active' : ''" :disabled="disabled">
                    <CIcon :icon="icon.cilXCircle" size="xl" />
                </CButton>
                <CButton type="button" color="success" @click="handlePumpButtonClick" variant="outline"
                    :class="state == 'WORKING' ? 'active' : ''" :disabled="disabled">
                    <CIcon :icon="icon.cilShower" size="xl" />
                </CButton>
                <CFormInput v-model="inputVolume" :id="deviceId + '-volume'" placeholder="&infin;" aria-label="Volume"
                    :aria-describedby="deviceId + '-inputVolumeText'" :disabled="disabled" />
                <CInputGroupText :id="deviceId + '-inputVolumeText'">ml</CInputGroupText>
                <CFormInput v-if="debug" v-model="inputSpeed" :id="deviceId + '-speed'" :placeholder="data.max_speed_rps" aria-label="Speed"
                    :aria-describedby="deviceId + '-inputSpeedText'" :disabled="disabled" />
                <CInputGroupText v-if="debug" :id="deviceId + '-inputSpeedText'">rps</CInputGroupText>
            </CInputGroup>
        </CCardBody>
    </CCard>
</template>

<script>
import { CCard, CCardBody, CInputGroup, CButton, CFormInput, CInputGroupText, CCardTitle } from '@coreui/vue'
import { CIcon } from '@coreui/icons-vue'
import * as icon from '@coreui/icons'
import { mapGetters, mapState } from 'vuex'

export default {
    name: 'PumpControl',
    components: {
        CCard,
        CCardBody,
        CButton,
        CFormInput,
        CIcon,
        CInputGroup,
        CInputGroupText,
        CCardTitle,
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
    setup() {
        return {
            icon,
        }
    },
    data() {
        return {
            inputVolume: "",
            inputSpeed: "",
        }
    },
    computed: {
        data() {
            const device = this.getDeviceById(this.deviceId)
            return device
        },
        stateText() {
            return this.data != null ? this.data.state_string : "Undefined"
        },
        state() {
            return this.data != null ? this.data.state_id : "UNDEFINED"
        },
        ...mapGetters("machine", [
            "getDeviceById",
        ]),
        ...mapState(["debug"]),
    },
    methods: {
        handlePumpButtonClick() {
            this.$store.dispatch("machine/runCommand", {
                device: "pump",
                command: "pump",
                deviceId: this.deviceId,
                volume: this.inputVolume,
                speed: this.inputSpeed,
            })
                .then((data) => {
                    console.debug(data)
                })
                .catch(err => {
                    this.$store.dispatch("notifyWarning", {
                        content: err.response.data
                    })
                })
        },
        handleStopButtonClick() {
            this.$store.dispatch("machine/runCommand", {
                device: "pump",
                command: "stop",
                deviceId: this.deviceId,
            })
                .then((data) => {
                    console.debug(data)
                })
                .catch(err => {
                    this.$store.dispatch("notifyWarning", {
                        content: err.response.data
                    })
                })
        },
    },
}
</script>

<style>
.btn {
    opacity: 50%;
}
.btn:hover {
    opacity: 80%;
}
.btn.active {
    opacity: 100%;
}
.btn.active:hover {
    opacity: 80%;
}
.btn:disabled {
    background-color: gray;
    border-color: gray;
    color: white;
    cursor: default;
    opacity: 80%;
}
</style>