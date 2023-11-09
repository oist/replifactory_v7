<template>
    <div class="MachineConnection" :class="{ 'device-disconnected': deviceConnected === false }">
        <div class="machine-busy-overlay" v-if="deviceBusy === true"></div>
        <template v-if="deviceConnected === false">
            <div class="connection-setup">
                <CForm class="row g-3">
                    <CCol xs="12">
                        <CFormLabel for="machineSelect">Machine</CFormLabel>
                        <CFormSelect v-model="selectedMachine" id="machineSelect" aria-label="Select machine"
                            @change="handleMachineSelected" :disabled="isConnected">
                            <option v-for="(value, key) in connectionOptions.device_address" :key="key" :value="key">
                                {{ value }}
                            </option>
                        </CFormSelect>
                    </CCol>
                    <CCol xs="12">
                        <CButton v-if="isDisconnected" @click="connectMachine" :disabled="loading" type="button" color="primary" variant="outline" class="w-100">
                            <CSpinner v-if="loading" size="sm" color="secondary" />
                            Connect
                        </CButton>
                        <CButton v-else @click="disconnectMachine" :disabled="loading" type="button" color="danger" variant="outline" class="w-100">
                            <CSpinner v-if="loading" size="sm" color="secondary" />
                            Disconnect
                        </CButton>
                    </CCol>
                    <CAlert v-if="error" color="danger" v-model="showAlert" @dismissed="onDismissed">{{ error }}</CAlert>
                </CForm>
            </div>
        </template>

        <template v-else>
            <p>Device Control Disabled - please pause experiment to control device.</p>
        </template>
    </div>
</template>

<script>
// import PumpControl from './PumpControl';
// import ValveControl from './ValveControl';
// import StirrerControl from './StirrerControl';
// import ODControl from './ODControl';
import { state } from "@/socket";
import { mapState, mapMutations, mapActions } from 'vuex';
import { CFormSelect, CButton, CFormLabel, CForm, CCol, CSpinner, CAlert } from '@coreui/vue';
// import { api } from "@/api";
import api from '@/api.js';


const DISCONNECTED_STATES = [
    "OFFLINE",
    "STATE_NONE",
    "STATE_CLOSED",
    "STATE_CLOSED_WITH_ERROR",
]


export default {
    components: {
        // PumpControl,
        // ValveControl,
        // StirrerControl,
        // ODControl,
        // CFormFloating,
        CFormSelect,
        CButton,
        CFormLabel,
        CForm,
        CCol,
        CSpinner,
        CAlert,
        // CFormSwitch,
    },
    computed: {
        ...mapState(['deviceConnected', 'deviceControlEnabled']),
        ...mapState('device', ['calibrationModeEnabled', 'stirrers', 'pumps', 'valves', 'ods']),
        connectionOptions() {
            let available_devices = state.connectionOptions
            console.log(available_devices)
            return available_devices
        },
        state() {
            return state.machine.state_id
        },
        isDisconnected() {
            return  DISCONNECTED_STATES.includes(state.machine.state_id)
        },
        isConnected() {
            return !this.isDisconnected
        },
    },
    data() {
        return {
            controlsVisible: false,
            selectedMachine: null,
            loading: false,
            error: '',
            showAlert: false,
        };
    },
    watch: {
        deviceControlEnabled(newVal) {
            if (newVal) {
                this.controlsVisible = true;
            } else {
                this.controlsVisible = false;
            }
        },
    },
    mounted() {
        // if not connected, try to connect
        // if (!this.deviceConnected) {
        //     this.connectDevice().then(() => {
        //         this.getAllDeviceData().then(() => {
        //         });
        //     });
        // }
    },
    methods: {
        ...mapMutations('device', ['toggleCalibrationMode', 'setDeviceControlEnabled']),
        ...mapActions('device', ['getAllDeviceData']),
        ...mapActions(['connectDevice']),
        handleMachineSelected(event) {
            this.selectedMachine = event.target.value
            // if (this.currentExperiment.status === 'running' || this.currentExperiment.status === 'paused') {
            //     await this.stopExperiment(this.currentExperiment.id);
            // }
            // const selectedExperimentId = event.target.value;
            // if (selectedExperimentId !== this.currentExperimentId) {
            //     this.currentExperimentId = selectedExperimentId;
            //     await this.setCurrentExperimentAction(this.currentExperimentId);
            // }
        },
        async disconnectMachine() {
            await this.connectCommand({
                command: "disconnect",
            })
        },
        async connectMachine() {
            await this.connectCommand({
                command: "connect",
                device_address: this.selectedMachine,
            })
        },
        async connectCommand(payload) {
            this.loading = true
            this.showAlert = false
            try {
                const response = await api.post('/connection', payload)
                console.log("Connection response: " + response)
                // do something with response.data
                this.loading = false
            } catch (err) {
                this.error = err.message
                this.showAlert = true
                this.loading = false
            }
        },
        onDismissed() {
            // do something when alert is dismissed
        },
    },
    sockets: {
        changeMachineListEvent() {

        },
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