<template>
    <div class="MachineState">
        <dl class="row">
            <dt>State</dt>
            <dd>{{ state_string }}</dd>
        </dl>
    </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
    computed: {
        ...mapState("machine", {
            state_string: state => state.machineState.string,
        }),
    },
};
</script>

<style scoped></style>
