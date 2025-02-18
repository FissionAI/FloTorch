<script setup lang="ts">

const props = defineProps<{
 experimentsData : any
 loading : boolean
}>()



</script>



<template>
    <div class="w-full">
    
      <UCard v-if="!loading">
      <template #header>
            <div class="flex justify-between items-center">
              <h2 class="text-xl font-medium">Experiment Details</h2>
              
            </div>
          </template>
        <table class="w-full">
        <tbody>
          <tr>
            <td class="font-medium">Experiment ID</td>
            <td>{{ props.experimentsData?.id }}</td>
          </tr>
          <tr>
            <td class="font-medium">Chunking</td>
            <td>{{ (props.experimentsData?.config?.bedrock_knowledge_base || !props.experimentsData?.config?.knowledge_base) ? 'NA' :  props.experimentsData?.config?.chunking_strategy }}</td>
          </tr>
          <tr>
            <td class="font-medium">Vector Dimensions</td>
            <td>{{ (props.experimentsData?.config?.bedrock_knowledge_base || !props.experimentsData?.config?.knowledge_base) ? 'NA' : props.experimentsData?.config?.vector_dimension }}</td>
          </tr>
          <tr>
            <td class="font-medium">Chunk Size</td>
            <td>{{ (props.experimentsData?.config?.bedrock_knowledge_base || !props.experimentsData?.config?.knowledge_base) ? 'NA' : useHumanChunkingStrategy(props.experimentsData?.config?.chunking_strategy) === 'Fixed' ? props.experimentsData?.config?.chunk_size : [props.experimentsData?.config?.hierarchical_child_chunk_size, props.experimentsData?.config?.hierarchical_parent_chunk_size]}}</td>
          </tr>
          <tr>
            <td class="font-medium">Chunk Overlap Percentage</td>
            <td>{{(props.experimentsData?.config?.bedrock_knowledge_base || !props.experimentsData?.config?.knowledge_base) ? 'NA' : useHumanChunkingStrategy(props.experimentsData?.config?.chunking_strategy) === 'Fixed' ? props.experimentsData?.config?.chunk_overlap : props.experimentsData?.config?.hierarchical_chunk_overlap_percentage}}</td>
          </tr>
          <tr>
            <td class="font-medium">N Shot Prompts</td>
            <td>{{ props.experimentsData?.config?.n_shot_prompts }}</td>
          </tr>
          <tr>
            <td class="font-medium">KNN</td>
            <td>{{props.experimentsData?.config?.knn_num }}</td>
          </tr>
          <tr>
            <td class="font-medium">Inferencing Model Temperature</td>
            <td>{{props.experimentsData?.config?.temp_retrieval_llm }}</td>
          </tr>
          <tr>
            <td class="font-medium">Indexing Algorithm</td>
            <td>{{(props.experimentsData?.config?.bedrock_knowledge_base || !props.experimentsData?.config?.knowledge_base) ? 'NA' : useHumanIndexingAlgorithm(props.experimentsData?.config?.indexing_algorithm!) }}</td>
          </tr>
          <tr>
            <td class="font-medium">Embedding Model</td>
            <td>{{ useModelName("indexing", props.experimentsData?.config?.embedding_model!) }} {{
              (props.experimentsData?.config?.bedrock_knowledge_base || !props.experimentsData?.config?.knowledge_base) ? 'NA' :
              `(${useHumanModelService(props.experimentsData?.config?.embedding_service!)})`
            }}
            </td>
          </tr>
          <tr>
            <td class="font-medium">Inferencing Model</td>
            <td>{{ useModelName("retrieval", props.experimentsData?.config?.retrieval_model!) }} ({{
              useHumanModelService(props.experimentsData?.config?.retrieval_service!) }})
            </td>
          </tr>
          <tr>
            <td class="font-medium">Reranking Model</td>
            <!-- <td>{{ 
             props.experimentsData?.config?.rerank_model_id! }}
            </td> -->
            <td>{{ props.experimentsData?.config?.rerank_model_id.includes('none') && props.experimentsData?.config?.knowledge_base !== 'true' ? 'NA' : props.experimentsData?.config?.rerank_model_id }}</td>
          </tr>
           <tr v-if="props.experimentsData?.config?.guardrail_name">
            <td class="font-medium">Guardrails</td>
            <td>{{
              props.experimentsData?.config?.guardrail_name }}
            </td>
          </tr>
           <tr v-if="props.experimentsData?.config?.kb_data">
            <td class="font-medium">Knowledge Base Data</td>
            <td>{{
             props.experimentsData?.config?.bedrock_knowledge_base === true ? props.experimentsData?.config?.kb_name : props.experimentsData?.config?.kb_data }}
            </td>
          </tr>
          <tr v-if="props.experimentsData?.config?.guardrail_id">
            <td class="font-medium">Guardrails ID</td>
            <td>{{
              props.experimentsData?.config?.guardrail_id }}
            </td>
          </tr>
          <tr v-if="props.experimentsData?.config?.guardrail_version">
            <td class="font-medium">Guardrail Version</td>
            <td> {{props.experimentsData?.config?.guardrail_version}}
            </td>
          </tr>
          <tr v-if="props.experimentsData?.config?.eval_embedding_model">
            <td class="font-medium">Evaluation Embedding Model</td>
            <td> {{props.experimentsData?.config?.eval_embedding_model}}
            </td>
          </tr>
          <tr v-if="props.experimentsData?.config?.eval_retrieval_model">
            <td class="font-medium">Evaluation Inferencing Model</td>
            <td> {{props.experimentsData?.config?.eval_retrieval_model}}
            </td>
          </tr>
        </tbody>
      </table>
      </UCard>
    </div>
</template>
