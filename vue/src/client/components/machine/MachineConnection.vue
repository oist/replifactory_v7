<template>
    <div class="connection-setup">
        <CForm class="row g-3">
            <CCol xs="12">
                <CFormLabel for="machineSelect">Machine</CFormLabel>
                <CFormSelect v-model="currentConnection.id" id="machineSelect" aria-label="Select machine"
                    @change="handleMachineSelected" :disabled="isConnected">
                    <option v-for="(value, device_id) in connectionOptions.devices" :key="device_id" :value="device_id">
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
import { mapState } from 'vuex';
import { CFormSelect, CButton, CFormLabel, CForm, CCol, CSpinner, CAlert } from '@coreui/vue';
import api from '@/api.js';

const DISCONNECTED_STATES = [
    "OFFLINE",
    "STATE_NONE",
    "STATE_CLOSED",
    "STATE_CLOSED_WITH_ERROR",
    "UNKNOWN",
]

export default {
    components: {
        CFormSelect,
        CButton,
        CFormLabel,
        CForm,
        CCol,
        CSpinner,
        CAlert,
    },
    computed: {
        isDisconnected() {
            return DISCONNECTED_STATES.includes(this.machineState.id)
        },
        isConnected() {
            return !this.isDisconnected
        },
        connectionOptions() {
            let options = {}
            let stateConnectedOptions = this.$store.state.machine.connection.options;
            if (this.isConnected && this.currentConnection !== undefined && !(this.currentConnection.id in options)) {
                options[this.currentConnection.id] = this.currentConnection
            }
            const result = {
                ...{
                    "devices": options,
                },
                ...stateConnectedOptions,
            };
            return result;
        },
        ...mapState('machine', {
            currentConnection: state => state.connection.current,
            machineState: state => state.machineState,
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
        handleMachineSelected(event) {
            this.selectedMachine = event.target.value
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
                    if (data.current.id !== null) {
                        this.selectedMachine = data.current.id
                    }
                })
                .catch(err => {
                    this.loading = false
                    this.error = err.message
                    this.showAlert = true
                })
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

<style scoped></style>
