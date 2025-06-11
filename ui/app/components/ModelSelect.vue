<script setup lang="ts">


const props = defineProps<{
  model: "embedding" | "retrieval";
  region?: string;
}>();

const meta = useProjectCreateMeta()

const items = computed(() => {
  if (props.model === "embedding") {
    return meta.indexingStrategy.embeddingService
  }
  if (props.model === "retrieval") {
    return props.region === 'us-west-2'? meta.retrievalStrategy.llmService.filter((item: any) => !item?.label.includes('Scout')) : meta.retrievalStrategy.llmService;
  }
  return [];
});

</script>



<template>
  <USelectMenu :items="items" multiple class="w-full primary-dropdown mt-1"/>
</template>
