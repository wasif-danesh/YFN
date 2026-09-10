<script setup>
defineProps({ name: { type: String, default: 'home' } })
const paths = {
  home: 'M3 10 12 2l9 8v11h-7v-7h-4v7H3Z',
  train:
    'M6 17h12V5c0-3-12-3-12 0v12Zm0-9h12M8 21l2-4m6 4-2-4M9 13h.01M15 13h.01',
  people:
    'M16 21v-3a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v3M17 4a4 4 0 0 1 0 8m3 9v-3a4 4 0 0 0-3-4M14 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z',
  leaf: 'M4 20c0-8 5-12 15-16 2 12-3 17-10 15M4 20 15 9',
  search: 'M21 21l-6-6M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z',
  arrow: 'M4 12h16m-6-6 6 6-6 6',
  pin: 'M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0ZM15 10a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z',
  close: 'm6 6 12 12M6 18 18 6',
}
</script>
<template>
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.7"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path :d="paths[name] || paths.home" />
  </svg>
</template>
