<template>
    <CCard style="width: 16rem" class="m-2">
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
                <CFormInput v-model="inputValue" :id="deviceId + '-volume'" placeholder="&infin;" aria-label="Volume"
                    :aria-describedby="deviceId + '-inputText'" :disabled="disabled" />
                <CInputGroupText :id="deviceId + '-inputText'">ml</CInputGroupText>
            </CInputGroup>
        </CCardBody>
    </CCard>
</template>

<script>
import { CCard, CCardBody, CInputGroup, CButton, CFormInput, CInputGroupText, CCardTitle } from '@coreui/vue'
import { CIcon } from '@coreui/icons-vue'
import * as icon from '@coreui/icons'
import { mapGetters } from 'vuex'

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
            inputValue: "",
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
    },
    methods: {
        handlePumpButtonClick() {
            this.$store.dispatch("machine/runCommand", {
                device: "pump",
                command: "pump",
                deviceId: this.deviceId,
                volume: this.inputValue,
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