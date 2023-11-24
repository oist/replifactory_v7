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
            state_string: state => state.data.state.text,
        }),
    },
};
</script>

<style scoped></style>
