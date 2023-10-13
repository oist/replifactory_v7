<template>
    <div class="DeviceTab" :class="{ 'device-disconnected': deviceConnected === false }">
        <div class="machine-busy-overlay" v-if="deviceBusy === true"></div>
        <!-- <div style="text-align: right;">
            <CFormSwitch label="Calibration Mode" id="formSwitchCheckChecked" v-model="calibrationModeEnabled"
                @change="toggleCalibrationMode" />
        </div> -->

        <template v-if="deviceControlEnabled || controlsVisible">
            <!-- <PumpControl />
            <ValveControl />
            <StirrerControl />
            <ODControl /> -->
        </template>

        <template v-if="deviceConnected === false">
            <div class="connection-setup">
                <div class="d-flex">
                    <CFormFloating class="flex-grow-1 mt-3">
                        <CFormSelect v-model="currentMachineId" id="machineSelect" floatingLabel="Select machine"
                            aria-label="Select machine" @change="handleMachineSelected">
                            <option v-for="machine in availableMachines" :key="machine.id" :value="machine.id">
                                {{ machine.name }}
                            </option>
                        </CFormSelect>
                    </CFormFloating>
                </div>
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
import { mapState, mapMutations, mapActions } from 'vuex';
import { CFormFloating, CFormSelect } from '@coreui/vue';


export default {
    components: {
        // PumpControl,
        // ValveControl,
        // StirrerControl,
        // ODControl,
        CFormFloating,
        CFormSelect,
        // CFormSwitch,
    },
    computed: {
        ...mapState(['deviceConnected', 'deviceControlEnabled']),
        ...mapState('device', ['calibrationModeEnabled', 'stirrers', 'pumps', 'valves', 'ods'])
    },
    data() {
        return {
            controlsVisible: false,
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
        async handleMachineSelected(event) {
            if (this.currentExperiment.status === 'running' || this.currentExperiment.status === 'paused') {
                await this.stopExperiment(this.currentExperiment.id);
            }
            const selectedExperimentId = event.target.value;
            if (selectedExperimentId !== this.currentExperimentId) {
                this.currentExperimentId = selectedExperimentId;
                await this.setCurrentExperimentAction(this.currentExperimentId);
            }
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