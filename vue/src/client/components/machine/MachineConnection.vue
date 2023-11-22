<template>
    <div class="connection-setup">
        <CForm class="row g-3">
            <CCol xs="12">
                <CFormLabel for="machineSelect">Machine</CFormLabel>
                <CFormSelect v-model="selectedMachine" id="machineSelect" aria-label="Select machine"
                    :disabled="isConnected">
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
import { mapState, mapGetters } from 'vuex';
import { CFormSelect, CButton, CFormLabel, CForm, CCol, CSpinner, CAlert } from '@coreui/vue';
import api from '@/api.js';


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
        connectionOptions() {
            let options = {}
            let stateConnectedOptions = this.$store.state.machine.connection.options;
            if (this.isConnected && this.currentConnection !== undefined && !(this.currentConnection.id in options)) {
                options[this.currentConnection.id] = this.currentConnection
                return {
                    ...stateConnectedOptions,
                    ...{
                        "devices": options,
                    },
                };
            }
            return stateConnectedOptions;
        },
        ...mapState("machine", {
            currentConnection: state => state.connection.current,
            machineState: state => state.machineState,
        }),
        ...mapGetters("machine", [
            "isDisconnected",
            "isConnected",
        ])
    },
    watch: {
        connectionOptions(newVal) {
            const options = newVal.devices
            if (this.isDisconnected && !(this.selectedMachine in options)) {
                const [firstDeviceId] = Object.keys(options)
                this.selectedMachine = firstDeviceId
            }
        },
        currentConnection(newVal) {
            if (newVal != null) {
                this.selectedMachine = newVal.id
            }
        },
    },
    data() {
        return {
            selectedMachine: undefined,
            loading: false,
            error: '',
            showAlert: false,
        };
    },
    mounted() {
        this.refreshConnectionOptions()
        this.selectedMachine = this.currentConnection.id
    },
    methods: {
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
                this.loading = false
            } catch (err) {
                this.error = err.response.data
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
                    if (data.current.id != null) {
                        this.selectedMachine = data.current.id
                    } else {
                        const [firstDeviceId] = Object.keys(data.options.devices)
                        this.selectedMachine = firstDeviceId
                    }
                })
                .catch(err => {
                    this.loading = false
                    this.error = err.response.data
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
