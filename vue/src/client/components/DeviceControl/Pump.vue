<template>
    <CCard :style="debug ? 'width: 24rem' : 'width: 16rem'" class="m-2 pump-control">
        <CCardBody>
            <CCardTitle>{{ label }}</CCardTitle>
            <CInputGroup class="mb-3 buttons-group">
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
            <CButton v-if="debug" color="primary" href="#" @click="motorProfileVisisble = !motorProfileVisisble">{{ motorProfileVisisble ? "Hide profile" : "Show profile" }}</CButton>
            <CCollapse :visible="motorProfileVisisble" v-if="debug">
                <CCard class="mt-3">
                <CCardBody>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-acceleration-text'">Acceleration (steps/sec²)</CInputGroupText>
                        <CFormInput type="number" min="14.55" max="59590" step="14.55" v-model="motor.profile.acceleration" :id="deviceId + '-profile-acceleration'" :aria-label="deviceId + ' acceleration'" :aria-describedby="deviceId + '-profile-acceleration-text'" :disabled="disabled"/>
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-deceleration-text'">Deceleration (steps/sec²)</CInputGroupText>
                        <CFormInput type="number" min="14.55" max="59590" step="14.55" v-model="motor.profile.deceleration" :id="deviceId + '-profile-deceleration'" :aria-label="deviceId + ' deceleration'" :aria-describedby="deviceId + '-profile-deceleration-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-max_speed_rps-text'">Max Speed (rps)</CInputGroupText>
                        <CFormInput type="number" min="0.07625" max="78.05" step="0.07625" v-model="motor.profile.max_speed_rps" :id="deviceId + '-profile-max_speed_rps'" :aria-label="deviceId + ' max speed rps'" :aria-describedby="deviceId + '-profile-max_speed_rps-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-min_speed_rps-text'">Min Speed (rps)</CInputGroupText>
                        <CFormInput type="number" min="0" max="4.8815" step="0.00119" v-model="motor.profile.min_speed_rps" :id="deviceId + '-profile-min_speed_rps'" :aria-label="deviceId + ' min speed rps'" :aria-describedby="deviceId + '-profile-min_speed_rps-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-full_step_speed-text'">Full Step Speed (rps)</CInputGroupText>
                        <CFormInput type="number" min="0.03815" max="78.125" step="0.07625" v-model="motor.profile.full_step_speed" :id="deviceId + '-profile-full_step_speed'" :aria-label="deviceId + ' full step speed'" :aria-describedby="deviceId + '-profile-full_step_speed-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-kval_hold-text'">Kval Hold (Vs x K)</CInputGroupText>
                        <CFormInput type="number" min="0" max="0.996" step="0.004" v-model="motor.profile.kval_hold" :id="deviceId + '-profile-kval_hold'" :aria-label="deviceId + ' kval hold'" :aria-describedby="deviceId + '-profile-kval_hold-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-kval_run-text'">Kval Run (Vs x K)</CInputGroupText>
                        <CFormInput type="number" min="0" max="0.996" step="0.004" v-model="motor.profile.kval_run" :id="deviceId + '-profile-kval_run'" :aria-label="deviceId + ' kval run'" :aria-describedby="deviceId + '-profile-kval_run-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-kval_acc-text'">Kval Acc (Vs x K)</CInputGroupText>
                        <CFormInput type="number" min="0" max="0.996" step="0.004" v-model="motor.profile.kval_acc" :id="deviceId + '-profile-kval_acc'" :aria-label="deviceId + ' kval acc'" :aria-describedby="deviceId + '-profile-kval_acc-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-kval_dec-text'">Kval Dec (Vs x K)</CInputGroupText>
                        <CFormInput type="number" min="0" max="0.996" step="0.004" v-model="motor.profile.kval_dec" :id="deviceId + '-profile-kval_dec'" :aria-label="deviceId + ' kval dec'" :aria-describedby="deviceId + '-profile-kval_dec-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-intersect_speed-text'">Intersect Speed (rps)</CInputGroupText>
                        <CFormInput type="number" min="0" max="4.8825" step="0.000298" v-model="motor.profile.intersect_speed" :id="deviceId + '-profile-intersect_speed'" :aria-label="deviceId + ' intersect speed'" :aria-describedby="deviceId + '-profile-intersect_speed-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-start_slope-text'">Start Slope (sec/step)</CInputGroupText>
                        <CFormInput type="number" min="0" max="0.004" step="0.000015" v-model="motor.profile.start_slope" :id="deviceId + '-profile-start_slope'" :aria-label="deviceId + ' start slope'" :aria-describedby="deviceId + '-profile-start_slope-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-acceleration_final_slope-text'">Acc Final Slope (sec/step)</CInputGroupText>
                        <CFormInput type="number" min="0" max="0.004" step="0.000015" v-model="motor.profile.acceleration_final_slope" :id="deviceId + '-profile-acceleration_final_slope'" :aria-label="deviceId + ' acceleration final slope'" :aria-describedby="deviceId + '-profile-acceleration_final_slope-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-deceleration_final_slope-text'">Dec Final Slope (sec/step)</CInputGroupText>
                        <CFormInput type="number" min="0" max="0.004" step="0.000015" v-model="motor.profile.deceleration_final_slope" :id="deviceId + '-profile-deceleration_final_slope'" :aria-label="deviceId + ' deceleration final slope'" :aria-describedby="deviceId + '-profile-deceleration_final_slope-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-thermal_compensation_factor-text'">Thermal Compensation Factor</CInputGroupText>
                        <CFormInput type="number" min="1" max="1.46875" step="0.03125" v-model="motor.profile.thermal_compensation_factor" :id="deviceId + '-profile-thermal_compensation_factor'" :aria-label="deviceId + ' thermal compensation factor'" :aria-describedby="deviceId + '-profile-thermal_compensation_factor-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-overcurrent_threshold-text'">Overcurrent Threshold (A)</CInputGroupText>
                        <CFormInput type="number" min="0.375" max="6" step="0.375" v-model="motor.profile.overcurrent_threshold" :id="deviceId + '-profile-overcurrent_threshold'" :aria-label="deviceId + ' overcurrent threshold'" :aria-describedby="deviceId + '-profile-overcurrent_threshold-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-stall_threshold-text'">Stall Threshold (A)</CInputGroupText>
                        <CFormInput type="number" min="0.3125" max="4" step="0.3125" v-model="motor.profile.stall_threshold" :id="deviceId + '-profile-stall_threshold'" :aria-label="deviceId + ' stall threshold'" :aria-describedby="deviceId + '-profile-stall_threshold-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-step_mode-text'">Step Mode</CInputGroupText>
                        <CFormInput type="number" min="0" max="7" step="1" v-model="motor.profile.step_mode" :id="deviceId + '-profile-step_mode'" :aria-label="deviceId + ' step mode'" :aria-describedby="deviceId + '-profile-step_mode-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-alarm_enable-text'">Alarm Enable</CInputGroupText>
                        <CFormInput v-model="motor.profile.alarm_enable" :id="deviceId + '-profile-alarm_enable'" :aria-label="deviceId + ' alarm enable'" :aria-describedby="deviceId + '-profile-alarm_enable-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CInputGroup class="mb-1">
                        <CInputGroupText :id="deviceId + '-profile-clockwise-text'">Clockwise</CInputGroupText>
                        <CFormInput v-model="motor.profile.clockwise" :id="deviceId + '-profile-clockwise'" :aria-label="deviceId + ' clockwise'" :aria-describedby="deviceId + '-profile-clockwise-text'" :disabled="disabled" />
                    </CInputGroup>
                    <CButton type="button" color="success" @click="handleSetProfileButtonClick" :disabled="disabled">
                        Save
                    </CButton>
                </CCardBody>
                </CCard>
            </CCollapse>
        </CCardBody>
    </CCard>
</template>

<script>
import { CCard, CCardBody, CInputGroup, CButton, CFormInput, CInputGroupText, CCardTitle, CCollapse } from '@coreui/vue'
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
        CCollapse,
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
            motor: {
                profile: {
                    acceleration: "",
                    deceleration: "",
                    max_speed_rps: "",
                    min_speed_rps: "",
                    full_step_speed: "",
                    kval_hold: "",
                    kval_run: "",
                    kval_acc: "",
                    kval_dec: "",
                    intersect_speed: "",
                    start_slope: "",
                    acceleration_final_slope: "",
                    deceleration_final_slope: "",
                    thermal_compensation_factor: "",
                    overcurrent_threshold: "",
                    stall_threshold: "",
                    step_mode: "",
                    alarm_enable: "",
                    clockwise: "",
                },
            },
            motorProfileVisisble: false,
        }
    },
    computed: {
        data() {
            const device = this.getDeviceById(this.deviceId)
            return device
        },
        motor_profile() {
            if (this.data != null && this.data.motor != null && this.data.motor.profile != null) {
                const profile_proxy = this.data.motor.profile
                return {
                    acceleration: profile_proxy["acceleration"],
                    deceleration: profile_proxy["deceleration"],
                    max_speed_rps: profile_proxy["max_speed_rps"],
                    min_speed_rps: profile_proxy["min_speed_rps"],
                    full_step_speed: profile_proxy["full_step_speed"],
                    kval_hold: profile_proxy["kval_hold"],
                    kval_run: profile_proxy["kval_run"],
                    kval_acc: profile_proxy["kval_acc"],
                    kval_dec: profile_proxy["kval_dec"],
                    intersect_speed: profile_proxy["intersect_speed"],
                    start_slope: profile_proxy["start_slope"],
                    acceleration_final_slope: profile_proxy["acceleration_final_slope"],
                    deceleration_final_slope: profile_proxy["deceleration_final_slope"],
                    thermal_compensation_factor: profile_proxy["thermal_compensation_factor"],
                    overcurrent_threshold: profile_proxy["overcurrent_threshold"],
                    stall_threshold: profile_proxy["stall_threshold"],
                    step_mode: profile_proxy["step_mode"],
                    alarm_enable: profile_proxy["alarm_enable"],
                    clockwise: profile_proxy["clockwise"],
                }
            }
            return this.motor.profile
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
    watch: {
        motor_profile(newVal) {
            this.motor.profile = newVal
        },
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
        handleSetProfileButtonClick() {
            this.$store.dispatch("machine/runCommand", {
                device: "pump",
                command: "set-profile",
                deviceId: this.deviceId,
                profile: this.motor.profile,
            })
                .then((data) => {
                    console.debug(data)
                })
                .catch(err => {
                    this.$store.dispatch("notifyWarning", {
                        content: err.response.data
                    })
                })
        }
    },
}
</script>

<style>
.pump-control .buttons-group .btn {
    opacity: 50%;
}
.pump-control .buttons-group .btn:hover {
    opacity: 80%;
}
.pump-control .buttons-group .btn.active {
    opacity: 100%;
}
.pump-control .buttons-group .btn.active:hover {
    opacity: 80%;
}
.pump-control .btn:disabled {
    background-color: gray;
    border-color: gray;
    color: white;
    cursor: default;
    opacity: 80%;
}
</style>