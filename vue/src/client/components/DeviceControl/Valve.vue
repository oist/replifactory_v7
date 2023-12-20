<template>
    <CButtonGroup class="valve-buttons" :vertical="vertical" size="sm" role="group" aria-label="Valve control buttons">
        <CButton color="danger" :class="closeButtonClasses" :disabled="disabled"
            v-c-tooltip="{ content: 'Close', placement: 'top' }" @click="close" variant="outline">
            <CIcon :icon="icon.cilX" size="xl" />
        </CButton>
        <CButton color="warning" :class="['BEETWEEN', 'OPENING', 'CLOSING'].includes(state) ? 'active' : ''"
            :disabled="disabled" v-c-tooltip="{ content: 'Beetween', placement: 'top' }" variant="outline">
            <CIcon :icon="icon.cilLoopCircular" size="xl" />
        </CButton>
        <CButton color="success" :class="openButtonClasses" :disabled="disabled"
            v-c-tooltip="{ content: 'Open', placement: 'top' }" @click="open" variant="outline">
            <CIcon :icon="icon.cilCheckAlt" size="xl" />
        </CButton>
    </CButtonGroup>
</template>

<script>
import { mapGetters } from 'vuex';
import { CButton, CButtonGroup } from '@coreui/vue'
import { CIcon } from '@coreui/icons-vue';
import * as icon from '@coreui/icons'

export default {
    name: 'ValveControl',
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
            default: "Valve",
        },
        deviceId: {
            type: String,
            required: true,
        },
    },
    components: {
        CButton,
        CButtonGroup,
        CIcon,
    },
    setup() {
        return {
            icon,
        }
    },
    computed: {
        closeButtonClasses() {
            let classes = ""
            if (this.vertical) {
                classes += "rounded-top-5"
            }
            if (this.state === "CLOSE") {
                classes += " active"
            }
            return classes
        },
        openButtonClasses() {
            let classes = ""
            if (this.vertical) {
                classes += "rounded-bottom-5"
            }
            if (this.state === "OPEN") {
                classes += " active"
            }
            return classes
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
        ...mapGetters("machine", [
            "getDeviceById",
        ])
    },
    methods: {
        toggle() {

        },
        test() {

        },
        async close() {
            await this.sendCommand("close")
        },
        async open() {
            await this.sendCommand("open")
        },
        async sendCommand(command) {
            this.loading = true
            this.showAlert = false
            this.$store.dispatch("machine/runCommand", {
                device: "valve",
                command: command,
                deviceId: this.deviceId,
            })
                .then((data) => {
                    console.debug(data)
                })
                .catch(err => {
                    this.loading = false
                    this.error = err.response.data
                    this.showAlert = true
                })
        },
    },
}
</script>

<style>
.valve-buttons .btn {
    opacity: 50%;
}

.valve-buttons .active {
    opacity: 100%;
}

.valve-buttons .btn:hover {
    opacity: 80%;
}

.valve-buttons .btn:active {
    opacity: 90%;
}

.valve-buttons .btn:disabled {
    background-color: gray;
    border-color: gray;
    color: white;
    cursor: default;
    opacity: 80%;
}
</style>