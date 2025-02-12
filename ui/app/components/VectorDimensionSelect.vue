<script setup lang="ts">

const meta = useProjectCreateMeta()

const options = computed(() => {
  return meta.indexingStrategy.vectorDimensions
})
</script>



<template>
  <USelectMenu :items="options" class="w-full primary-dropdown" value-key="value" multiple />
</template>
