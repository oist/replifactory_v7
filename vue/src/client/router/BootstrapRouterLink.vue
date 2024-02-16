<template>
  <router-link v-slot="{ isActive, href, navigate }" v-bind="$props" custom>
    <li class="nav-item">
      <a
        v-bind="$attrs"
        :href="href"
        class="nav-link"
        :class="isActive ? activeClass : inactiveClass"
        @click="navigate"
      >
        <slot />
      </a>
    </li>
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
      default: "active",
    },
    inactiveClass: {
      type: String,
      default: "",
    },
  },
};
</script>
