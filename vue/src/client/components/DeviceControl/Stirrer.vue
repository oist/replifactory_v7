<template>
    <div>
        <CFormRange v-model="value" :min="min" :max="max" :step="step" @input="handleChange" :disabled="disabled" />
        <span>{{ value }}</span>
    </div>
</template>

<script>
import { CFormRange } from '@coreui/vue';

export default {
    name: "StirrerControl",
    components: {
        CFormRange,
    },
    props: {
        disabled: {
            type: Boolean,
            default: false,
        },
        deviceId: {
            type: String,
            required: true,
        },
    },
    data() {
        return {
            value: 0,
            min: 0,
            max: 100,
            step: 1,
        };
    },
    methods: {
        handleChange(event) {
            console.debug(event);
            this.$store.dispatch("machine/runCommand", {
                device: "stirrer",
                command: "setSpeed",
                deviceId: this.deviceId,
                speed: event.target.value,
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
};
</script>
