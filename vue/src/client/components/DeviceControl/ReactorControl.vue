<template>
    <CCard style="width: 18rem" class="m-2">
        <CCardBody>
            <CCardTitle>Reactor N</CCardTitle>
            <CCardSubtitle class="mb-2 text-muted">Lactobacillus plantarum</CCardSubtitle>
            <!-- <CCardText>
                Some quick example text to build on the card title and make up the bulk of the card's content.
            </CCardText> -->
            <!-- <PumpControl :disabled="!deviceControlEnabled" /> -->
            <VialControl :disabled="disabled" />
            <!-- <ValvesGroupControl :disabled="!deviceControlEnabled" /> -->
            <!-- <ValveControl :disabled="!deviceControlEnabled" /> -->
            <!-- <StirrerControl :disabled="!deviceControlEnabled" /> -->
            <!-- <ODControl :disabled="!deviceControlEnabled" /> -->
        </CCardBody>
    </CCard>
</template>

<script>
// import PumpControl from './PumpControl';
// import ValvesGroupControl from './ValvesGroupControl';
// import ValveControl from './ValveControl';
// import StirrerControl from './StirrerControl';
// import ODControl from './ODControl';
import VialControl from './VialControl';
import { CCard, CCardBody, CCardTitle, CCardSubtitle } from '@coreui/vue'


export default {
    components: {
        // PumpControl,
        // ValvesGroupControl,
        // ValveControl,
        // StirrerControl,
        // ODControl,
        VialControl,
        // CFormSwitch,
        CCard,
        CCardBody,
        CCardTitle,
        CCardSubtitle,
        // CCardText,
    },
    props: {
        disabled: {
            type: Boolean,
            default: false,
        },
    },
}
</script>

<style></style>