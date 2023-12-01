<template>
    <Valve class="mx-4 my-1" v-for="i in 7" :deviceId="'valve-' + (i-1)" :key="i" :title="'Valve ' + i" :disabled="disabled"></Valve>
</template>

<script>
import Valve from './Valve';

export default {
    name: 'ValvesGroupControl',
    props: {
        disabled: {
            type: Boolean,
            default: false,
        }
    },
    components: {
        Valve
    },
}
</script>

<style></style>