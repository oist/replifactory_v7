<template>
  <router-link v-slot="{ href, navigate }" v-bind="$props" custom>
    <a v-bind="$attrs" :href="href" :class="isActive ? activeClass : inactiveClass" @click="navigate">
      <slot />
    </a>
  </router-link>
</template>

<script setup>
import { computed, defineProps } from 'vue';
import { useRoute, RouterLink } from 'vue-router';

const props = defineProps({
  ...RouterLink.props,
  activeClass: {
    type: String,
    default: "active border-bottom border-4",
  },
  inactiveClass: {
    type: String,
    default: "",
  },
  alias: {
    type: String,
    default: "",
  },
});

const route = useRoute();

const isActive = computed(() => {
  const target = props.to;
  const targetPath = typeof target === 'string' ? target : target.path;
  const targetName = typeof target === 'object' ? target.name : null;
  const targetAlias = props.alias; // Access the alias from props

  // Special handling for root path '/'
  if (targetPath === '/' || targetAlias !== "") {
    return route.path === '/' || route.path === targetAlias;
  }

  // Check if the current route matches the target by name, path, or alias
  const isExactMatch = route.name === targetName || route.path === targetPath || route.path === targetAlias;

  // Check if any parent routes match the target or alias, excluding the root alias scenario
  const isParentMatch = route.matched.some(r => {
    const matchPath = r.path === '' ? '/' : r.path; // Normalize root path
    // Ensure not to match root alias by checking against the target path, name, and alias
    return (targetPath !== '/' && targetAlias !== '/' && ((targetName && r.name === targetName) || (targetPath && matchPath === targetPath) || (targetAlias && matchPath === targetAlias)));
  });

  return isExactMatch || isParentMatch;
});
</script>

<style scoped>
.active {
  border-color: #6f42c1 !important;
}
</style>
