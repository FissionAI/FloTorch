<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query';


const props = defineProps<{
  projectId: string,
  config?: ProjectExperiment[]
}>()

const { data: project, isLoading } = useQuery({
  queryKey: ["project", props.projectId],
  queryFn: () => useProject(props.projectId)
})

const config = computed(() => {
  return project.value?.config
})

const handleDownload = () => {
  console.log(config.value)
  console.log(props.config)
  const sampleConfig = {
    ...config.value,
      indexing: {
        chunking_strategy: [...new Set([...props.config.map(exp => exp.chunking_strategy)])],
        vector_dimension: [...new Set([...props.config.map(exp => exp.vector_dimension)])],
        indexing_algorithm: [...new Set([...props.config.map(exp => exp.indexing_algorithm)])],
        ...([...new Set([...props.config.map(exp => exp.chunk_overlap)])].includes(null) ? {} : {chunk_overlap: [...new Set([...props.config.map(exp => exp.chunk_overlap)])]}),
        ...([...new Set([...props.config.map(exp => exp.chunk_size)])].includes(null) ? {} : {chunk_size: [...new Set([...props.config.map(exp => exp.chunk_size)])]}),
        ...([...new Set([...props.config.map(exp => exp.hierarchical_child_chunk_size)])].includes(null) ? {} : {hierarchical_child_chunk_size: [...new Set([...props.config.map(exp => exp.hierarchical_child_chunk_size)])]}),
        ...([...new Set([...props.config.map(exp => exp.hierarchical_parent_chunk_size)])].includes(null) ? {} : {hierarchical_parent_chunk_size: [...new Set([...props.config.map(exp => exp.hierarchical_parent_chunk_size)])]}),
        ...([...new Set([...props.config.map(exp => exp.hierarchical_chunk_overlap_percentage)])].includes(null) ? {} : {hierarchical_chunk_overlap_percentage: [...new Set([...props.config.map(exp => exp.hierarchical_chunk_overlap_percentage)])]}),
        embedding: [...new Set([...props.config.map(exp => {
          return {
            model: exp.embedding_model,
            service: exp.embedding_service,
            label: useModelName("indexing", exp.embedding_model)
          }
        })])]
      },
      retrieval: {
        rerank_model_id: [...new Set([...props.config.map(exp => exp.retrieval_model)])],
        n_shot_prompts: [...new Set([...props.config.map(exp => exp.n_shot_prompts)])],
        retrieval: props.config.map(exp => {
          return {
            model: exp.retrieval_model,
            service: exp.retrieval_service,
            label: useModelName("retrieval", exp.retrieval_model)
          }
        }),
        knn_num: [...new Set([...props.config.map(exp => exp.knn_num)])],
        temp_retrieval_llm: [...new Set([...props.config.map(exp => exp.temp_retrieval_llm)])],
      }
  }
  console.log(sampleConfig)

  // const blob = props.config ? new Blob([JSON.stringify(sampleConfig)], { type: 'application/json' }) : new Blob([JSON.stringify(config.value)], { type: 'application/json' })
  // const link = document.createElement("a");
  // link.download = `${project.value?.id}_config.json`;
  // link.href = URL.createObjectURL(blob)
  // link.dataset.downloadurl = ["text/json", link.download, link.href].join(":");
  // const evt = new MouseEvent("click", {
  //   view: window,
  //   bubbles: true,
  //   cancelable: true,
  // });
  // link.dispatchEvent(evt);
  // link.remove()
}
</script>



<template>
  <UButton icon="i-lucide-download" label="Download Config" :loading="isLoading" @click="handleDownload" />
</template>
