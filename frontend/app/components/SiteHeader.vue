<script setup>
defineProps({ compareTo: { type: [String, Object], default: '/compare' } })
</script>
<template>
  <a href="#main" class="skip-link">Skip to content</a>
  <header class="renter-header">
    <NuxtLink to="/" class="brand"
      ><SiteIcon name="home" /><span
        >Your Friendly<br class="brand-break" />
        Neighbourhood</span
      ></NuxtLink
    >
    <nav aria-label="Main navigation">
      <NuxtLink to="/" active-class="active" exact-active-class="active"
        >Home</NuxtLink
      ><NuxtLink :to="compareTo" active-class="active">Compare areas</NuxtLink>
    </nav>
  </header>
</template>
