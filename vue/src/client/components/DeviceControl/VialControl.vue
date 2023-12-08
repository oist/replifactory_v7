<template>
    <div class="progress progress-bar-vertical">
        <div class="progress-bar" role="progressbar" aria-valuenow="30" aria-valuemin="0" aria-valuemax="100"
            style="height: 30%;">
            <span class="sr-only">30% Complete</span>
        </div>
    </div>
</template>

<script>

export default {
    name: 'ValvesGroupControl',
    props: {
        disabled: {
            type: Boolean,
            default: false,
        },
        width: {
            type: String,
            default: "75px",
        },
        height: {
            type: String,
            default: "160px",
        }
    },
    components: {

    },
}
</script>

<style>
.progress-bar-vertical {
    width: 20px;
    min-height: 100px;
    display: flex;
    align-items: flex-end;
    margin-right: 20px;
    float: left;
}

.progress-bar-vertical .progress-bar {
    width: 100%;
    height: 0;
    -webkit-transition: height 0.6s ease;
    -o-transition: height 0.6s ease;
    transition: height 0.6s ease;
}
</style>