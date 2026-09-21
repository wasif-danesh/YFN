<script setup>
// Loading message that explains longer waits, e.g. while the free-plan API wakes up.
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
const props = defineProps({
  label: { type: String, default: 'Loading…' },
  hint: { type: String, default: '' },
  slowAfter: { type: Number, default: 5000 },
  verySlowAfter: { type: Number, default: 30000 },
})
const stage = ref(0)
let timers = []
const message = computed(() => {
  if (stage.value === 2)
    return {
      title: 'Almost there…',
      detail: 'Thanks for waiting. There’s no need to refresh the page.',
    }
  if (stage.value === 1)
    return {
      title: 'Starting the area service…',
      detail: ['The first visit can take up to a minute.', props.hint]
        .filter(Boolean)
        .join(' '),
    }
  return { title: props.label, detail: '' }
})
onMounted(() => {
  timers = [
    setTimeout(() => (stage.value = 1), props.slowAfter),
    setTimeout(() => (stage.value = 2), props.verySlowAfter),
  ]
})
onBeforeUnmount(() => timers.forEach(clearTimeout))
</script>
<template>
  <div class="loading-status" role="status">
    <span class="loading-spinner" aria-hidden="true"></span>
    <p>
      <strong>{{ message.title }}</strong>
      <span v-if="message.detail">{{ message.detail }}</span>
    </p>
  </div>
</template>
