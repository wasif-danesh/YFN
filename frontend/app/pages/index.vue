<script setup>
import ApiConsole from '~/components/ApiConsole.vue'
const config = useRuntimeConfig()
</script>

<template>
  <ApiConsole :api-base="config.public.apiBase" />
</template>
