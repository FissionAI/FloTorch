<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query';


const props = defineProps<{
  projectId: string
  experimentId: string
}>()

const isOpen = ref(false)

const { data: experiment } = useQuery({
  queryKey: ["experiments", toRef(props, "experimentId"), toRef(props, "projectId")],
  queryFn: () => useProjectExperiment(props.projectId, props.experimentId)
})



</script>



<template>
  <UButton label="Details" icon="i-lucide-info" @click="isOpen = true" />
  <UModal class="overflow-y-scroll max-h-[50vh]" v-model:open="isOpen" title="Experiment Details" description="More details about the experiment">
    <template #body>
      <table class="w-full">
        <tbody>
          <tr>
            <td class="font-medium">Experiment ID</td>
            <td>{{ experiment?.id }}</td>
          </tr>
          <tr>
            <td class="font-medium">Chunking</td>
            <td>{{ experiment?.config?.chunking_strategy }}</td>
          </tr>
          <tr>
            <td class="font-medium">Vector Dimensions</td>
            <td>{{ experiment?.config?.vector_dimension }}</td>
          </tr>
          <tr>
            <td class="font-medium">Chunk Size</td>
            <td>{{ useHumanChunkingStrategy(experiment?.config?.chunking_strategy) === 'Fixed' ? experiment?.config?.chunk_size : [experiment?.config?.hierarchical_child_chunk_size, experiment?.config?.hierarchical_parent_chunk_size]}}</td>
          </tr>
          <tr>
            <td class="font-medium">Chunk Overlap Percentage</td>
            <td>{{ useHumanChunkingStrategy(experiment?.config?.chunking_strategy) === 'Fixed' ? experiment?.config?.chunk_overlap : experiment?.config?.hierarchical_chunk_overlap_percentage}}</td>
          </tr>
          <tr>
            <td class="font-medium">N Shot Prompts</td>
            <td>{{ experiment?.config?.n_shot_prompts }}</td>
          </tr>
          <tr>
            <td class="font-medium">KNN</td>
            <td>{{ experiment?.config?.knn_num }}</td>
          </tr>
          <tr>
            <td class="font-medium">Inferencing LLM Temperature</td>
            <td>{{ experiment?.config?.temp_retrieval_llm }}</td>
          </tr>
          <tr>
            <td class="font-medium">Indexing Algorithm</td>
            <td>{{ useHumanIndexingAlgorithm(experiment?.config?.indexing_algorithm!) }}</td>
          </tr>
          <tr>
            <td class="font-medium">Embedding Model</td>
            <td>{{ useModelName("indexing", experiment?.config?.embedding_model!) }} ({{
              useHumanModelService(experiment?.config?.embedding_service!) }})
            </td>
          </tr>
          <tr>
            <td class="font-medium">Inferencing LLM</td>
            <td>{{ useModelName("retrieval", experiment?.config?.retrieval_model!) }} ({{
              useHumanModelService(experiment?.config?.retrieval_service!) }})
            </td>
          </tr>
          <tr v-if="experiment?.config?.guardrail_id">
            <td class="font-medium">Guardrails ID</td>
            <td>{{
              experiment?.config?.guardrail_id }}
            </td>
          </tr>
          <tr v-if="experiment?.config?.guardrail_version">
            <td class="font-medium">Guardrail Version</td>
            <td> {{experiment?.config?.guardrail_version}}
            </td>
          </tr>
        </tbody>
      </table>
    </template>
  </UModal>
</template>
