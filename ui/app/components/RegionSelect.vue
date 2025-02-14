<script setup lang="ts">

const meta = useProjectCreateMeta()

const regions = computed(() => {
  return meta.dataStrategy.regions
})

</script>



<template>
  <USelectMenu :search-input="false" :items="regions" class="w-full primary-dropdown" value-key="value" />
</template>
