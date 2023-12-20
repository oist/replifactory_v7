<template>
    <CCard style="width: 18rem" class="m-2">
        <CCardBody>
            <CCardTitle>{{ reactor.title }}</CCardTitle>
            <CCardSubtitle class="mb-2 text-muted">{{ reactor.subtitle }}</CCardSubtitle>
            <!-- <CCardText>
                Some quick example text to build on the card title and make up the bulk of the card's content.
            </CCardText> -->
            <!-- <PumpControl :disabled="!deviceControlEnabled" /> -->
            <VialControl :disabled="disabled" />
            <Valve class="mx-4 my-1" :deviceId="valve.id" :key="valve.id" :title="valve.title" :disabled="disabled" />
            <!-- <ValvesGroupControl :disabled="!deviceControlEnabled" /> -->
            <!-- <ValveControl :disabled="!deviceControlEnabled" /> -->
            <!-- <StirrerControl :disabled="!deviceControlEnabled" /> -->
            <!-- <ODControl :disabled="!deviceControlEnabled" /> -->
            <!-- <RangeSlider></RangeSlider> -->
            <Stirrer :deviceId="stirrer.id" :key="stirrer.id" :title="stirrer.title" :disabled="disabled" />
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
import Valve from './Valve';
import Stirrer from './Stirrer';
// import RangeSlider from '@/client/components/widgets/RangeSlider';
import { CCard, CCardBody, CCardTitle, CCardSubtitle } from '@coreui/vue'


export default {
    components: {
        // PumpControl,
        // ValvesGroupControl,
        // ValveControl,
        // StirrerControl,
        // ODControl,
        VialControl,
        Valve,
        Stirrer,
        // RangeSlider,
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
        id: {
            type: Number,
            default: 0,
        },
        title: {
            type: String,
            default: null,
        },
        subtitle: {
            type: String,
            default: null,
        },
        valveId: {
            type: String,
            default: null,
        },
        valveTitle: {
            type: String,
            default: null,
        },
        stirrerId: {
            type: String,
            default: null,
        },
        stirrerTitle: {
            type: String,
            default: null,
        },
    },
    computed: {
        reactor() {
            return {
                id: this.id,
                title: this.title != null ? this.title : `Reactor ${this.id}`,
                subtitle: this.subtitle != null ? this.subtitle : `Lactobacillus plantarum`,
            }
        },
        valve() {
            return {
                id: this.valveId != null ? this.valveId : `valve-${this.id}`,
                title: this.valveTitle != null ? this.valveTitle : `Valve ${this.id}`,
            }
        },
        stirrer() {
            return {
                id: this.stirrerId != null ? this.stirrerId : `stirrer-${this.id}`,
                title: this.stirrerTitle != null ? this.stirrerTitle : `Stirrer ${this.id}`,
            }
        },
    }
}
</script>

<style></style>