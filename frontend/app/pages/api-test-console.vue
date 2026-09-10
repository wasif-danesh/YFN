<script setup>
import ApiConsole from '~/components/ApiConsole.vue'
const config = useRuntimeConfig()
useSeoMeta({
  title: 'API test console | Your Friendly Neighbourhood',
  robots: 'noindex, nofollow',
})
</script>

<template>
  <ApiConsole :api-base="config.public.apiBase" />
</template>
