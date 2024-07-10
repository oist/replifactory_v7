<template>
  <router-link v-slot="{ isActive, href, navigate }" v-bind="$props" custom>
    <a v-bind="$attrs" :href="href" :class="isActive ? activeClass : inactiveClass" @click="navigate">
      <slot />
    </a>
  </router-link>
</template>

<script>
import { RouterLink } from "vue-router";

export default {
  name: "BootstrapRouterLink",
  inheritAttrs: false,
  props: {
    ...RouterLink.props,
    activeClass: {
      type: String,
      default: "active border-bottom border-4",
    },
    inactiveClass: {
      type: String,
      default: "",
    },
  },
};
</script>

<style scoped>
.active {
  border-color: #6f42c1 !important;
}
</style>
