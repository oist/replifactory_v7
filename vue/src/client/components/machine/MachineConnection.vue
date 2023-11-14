<template>
    <div class="connection-setup">
        <CForm class="row g-3">
            <CCol xs="12">
                <CFormLabel for="machineSelect">Machine</CFormLabel>
                <CFormSelect v-model="selectedMachine" id="machineSelect" aria-label="Select machine"
                    @change="handleMachineSelected" :disabled="isConnected">
                    <option v-for="(value, key) in connectionOptions.devices" :key="key" :value="key">
                        {{ value.product }} ({{ value.serial_number }})
                    </option>
                </CFormSelect>
            </CCol>
            <CCol xs="12">
                <CButton v-if="isDisconnected" @click="connectMachine" :disabled="loading" type="button" color="primary"
                    variant="outline" class="w-100">
                    <CSpinner v-if="loading" size="sm" color="secondary" />
                    Connect
                </CButton>
                <CButton v-else @click="disconnectMachine" :disabled="loading" type="button" color="danger"
                    variant="outline" class="w-100">
                    <CSpinner v-if="loading" size="sm" color="secondary" />
                    Disconnect
                </CButton>
            </CCol>
            <CAlert v-if="error" color="danger" v-model="showAlert" @dismissed="onDismissed">{{ error }}</CAlert>
        </CForm>
    </div>
</template>

<script>
import { state } from "@/socket";
import { mapState } from 'vuex';
import { CFormSelect, CButton, CFormLabel, CForm, CCol, CSpinner, CAlert } from '@coreui/vue';
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
        devices() {
            return state.connectionOptions.devices
        },
        // ...mapState(['deviceConnected', 'deviceControlEnabled']),
        // ...mapState('device', ['calibrationModeEnabled', 'stirrers', 'pumps', 'valves', 'ods']),
        connectionOptions() {
            let options = state.connectionOptions
            console.log(options)
            return options
        },
        state() {
            return state.machine.state_id
        },
        isDisconnected() {
            return DISCONNECTED_STATES.includes(state.machine.state_id)
        },
        isConnected() {
            return !this.isDisconnected
        },
        ...mapState('machine', {
            connectionOptions: state => state.connection.options,
            currentConnection: state => state.connection.current
        })
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
        this.refreshConnectionOptions()
    },
    methods: {
        // ...mapMutations('device', ['toggleCalibrationMode', 'setDeviceControlEnabled']),
        // ...mapActions('device', ['getAllDeviceData']),
        // ...mapActions(['connectDevice']),
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
                device_id: this.selectedMachine,
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
        refreshConnectionOptions() {
            this.loading = true
            this.showAlert = false
            this.$store.dispatch("machine/updateConnection")
                .then((data) => {
                    this.loading = false
                    if (data.current.device_id !== null) {
                        this.selectedMachine = data.current.device_id
                    }
                })
                .catch(err => {
                    this.loading = false
                    this.error = err.message
                    this.showAlert = true
                })
        },
        // async getConnectionOptions() {
        //     this.loading = true
        //     this.showAlert = false
        //     try {
        //         const response = await api.get('/connection')
        //         console.debug(response)
        //         state.connectionOptions = response.data.options
        //         state.currentConnection = response.data.current
        //         this.selectedMachine = response.data.current.device_address
        //     } catch (err) {
        //         this.error = err.message
        //         this.showAlert = true
        //         this.loading = false
        //     }
        // },
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

<style scoped></style>