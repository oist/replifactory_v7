<template>
    <CButtonGroup class="valve-buttons" vertical size="sm" role="group" aria-label="Valve control buttons">
        <CButton color="danger" class="rounded-top-5" :class="state === 'CLOSE' ? 'active' : ''" :disabled="disabled"
            v-c-tooltip="{ content: 'Close', placement: 'right' }"
            @click="close">
            <CIcon :icon="icon.cilX" size="xl" />
        </CButton>
        <CButton color="warning" :class="['BEETWEEN', 'OPENING', 'CLOSING'].includes(state) ? 'active' : ''" :disabled="disabled"
            v-c-tooltip="{ content: 'Beetween', placement: 'right' }">
            <CIcon :icon="icon.cilLoopCircular" size="xl" />
        </CButton>
        <CButton color="success" class="rounded-bottom-5" :class="state === 'OPEN' ? 'active' : ''" :disabled="disabled"
            v-c-tooltip="{ content: 'Open', placement: 'right' }"
            @click="open">
            <CIcon :icon="icon.cilCheckAlt" size="xl" />
        </CButton>
    </CButtonGroup>
</template>

<script>
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
        data() {
            return this.$store.state.machine.data.devices[this.deviceId];
        },
        stateText() {
            return this.data != null ? this.data.state_string : "Undefined";
        },
        state() {
            return this.data != null ? this.data.state_id : "UNDEFINED";
        },
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
                    // this.loading = false
                    // if (data.current.id != null) {
                    //     this.selectedMachine = data.current.id
                    // } else {
                    //     const [firstDeviceId] = Object.keys(data.options.devices)
                    //     this.selectedMachine = firstDeviceId
                    // }
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