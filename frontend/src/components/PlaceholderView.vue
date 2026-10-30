<script setup lang="ts">
defineProps<{ code: string; title: string }>()
</script>

<template>
  <main class="placeholder">
    <p class="placeholder__code">{{ code }}</p>
    <h1>{{ title }}</h1>
    <p>Pantalla pendiente de diseño (PEND-01).</p>
  </main>
</template>

<style scoped>
.placeholder {
  max-width: 28rem;
  margin: 0 auto;
  padding: 1.5rem 1rem;
}
.placeholder__code {
  margin: 0;
  color: var(--p-text-muted-color);
}
</style>
