<template>
    <router-link v-bind="$props" custom v-slot="{ isActive, href, navigate }">
        <li class="nav-item">
            <a v-bind="$attrs" :href="href" @click="navigate" class="nav-link"
                :class="isActive ? activeClass : inactiveClass">
                <slot />
            </a>
        </li>
    </router-link>
</template>

<script>
import { RouterLink } from 'vue-router';

export default {
    name: "BootstrapRouterLink",
    inheritAttrs: false,
    props: {
        ...RouterLink.props,
        activeClass: {
            type: String,
            default: "active",
        },
        inactiveClass: {
            type: String,
            default: "",
        },
    },
}
</script>