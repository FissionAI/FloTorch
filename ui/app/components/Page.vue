<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router';

const props = defineProps<{
  title: string;
  description?: string;
  to?: RouteLocationRaw
}>();

const route = useRoute()
const showHomeButton = computed(() => {
  return route.name !== 'projects'
})
</script>



<template>
  <div class="flex justify-between items-center">
    <div class="flex gap-2 items-center">
      <!-- <UButton v-if="showHomeButton" icon="i-lucide-house" :to="{ name: 'projects' }" square /> -->
      <div>
        <h2>
          <NuxtLink :to="props.to" class="text-2xl font-bold">{{ props.title }}</NuxtLink>
        </h2>
        <p v-if="props.description" class="text-sm text-gray-500">{{ props.description }}</p>
      </div>
    </div>

    <div>
      <div class="flex gap-2 items-center">
        <slot name="actions" />
      </div>
    </div>
  </div>
  <div class="mt-4">
    <slot />
  </div>
</template>
