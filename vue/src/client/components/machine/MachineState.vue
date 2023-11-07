<template>
    <div class="MachineState">
        <dl class="row">
            <dt>State</dt>
            <dd>{{ state_string }}</dd>
        </dl>
    </div>
</template>

<script>
import { state } from '@/socket';

export default {
    computed: {
        state_string() {
            return state.machine.state_string
        }
    },
};
</script>

<style scoped>

</style>