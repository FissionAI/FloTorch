<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router';

const props = defineProps<{
  title: string;
  description?: string;
  to?: RouteLocationRaw,
  hideSlot? : boolean;
}>();

const route = useRoute()
const showHomeButton = computed(() => {
  return route.name !== 'projects'
})


</script>



<template>
  <div class="flex justify-between items-center">
    <div class="flex gap-2 items-center" v-if="hideSlot">
      <!-- <UButton v-if="showHomeButton" icon="i-lucide-house" :to="{ name: 'projects' }" square /> -->
      <div>
        <h2>
          <NuxtLink :to="props.to" :class="route.name === 'projects-id' && props.to?.name === 'projects-id' ? 'cursor-default' : ''" class="text-2xl font-bold ml-1">{{ props.title }}</NuxtLink>
        </h2>
        <p v-if="props.description" class="text-sm text-gray-500 ml-1">{{ props.description }}</p>
      </div>
    </div>

    <div class="w-full" v-if="!hideSlot">
      <div class="flex gap-2 items-center w-full">
        <slot name="actions" />
      </div>
    </div>
  </div>
  <div class="mt-4">
    <slot />
  </div>
</template>
