<script setup lang="ts">


const props = defineProps<{
  model: "embedding" | "retrieval";
}>();

const meta = useProjectCreateMeta()

const items = computed(() => {
  if (props.model === "embedding") {
    return meta.indexingStrategy.embeddingService
  }
  if (props.model === "retrieval") {
    return meta.retrievalStrategy.llmService
  }
  return [];
});

</script>



<template>
  <USelectMenu :items="items" multiple class="w-full primary-dropdown" />
</template>
