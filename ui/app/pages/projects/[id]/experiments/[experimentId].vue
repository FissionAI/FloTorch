<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
import { useQuery, useMutation } from "@tanstack/vue-query";
const experimentId = useRouteParams<string>("experimentId");

const project = inject<Ref<Project>>("project");
const experimentsData = ref([]);
const experimentsSharedData = useState('experimentsData', () => []);

const { data: questionMetrics, isLoading } = useQuery({
  queryKey: ["projects", project, "question-metrics"],
  queryFn: () =>
    useProjectExperimentQuestionMetrics(project!.value?.id, experimentId.value),
});

 const { mutateAsync: fetchExperimentsData, isPending: isLoadingExperiments } = useMutation({
    mutationFn: async () => {
      experimentsData.value = await useProjectExperiment(project!.value.id, experimentId.value);
      experimentsSharedData.value = experimentsData.value;
      return experimentsData.value
    }
    })

onMounted(() => {
  fetchExperimentsData();
});

onUnmounted(() => {
  experimentsSharedData.value = [];
})

useHead({
  title: "Question Metrics",
});

const columns = ref<TableColumn<ExperimentQuestionMetric>[]>([
  {
    header: "S.No",
    accessorKey: "sno"
   },
  {
    header: "Question",
    accessorKey: "question",
  },
  {
    header: "Ground Truth",
    accessorKey: "gt_answer",
  },
  {
    header: "Generated Answer",
    accessorKey: "generated_answer",
  },
  {
    header: "Guardrails User Query",
    accessorKey: "guardrail_input_assessment",
  },
  {
    header: "Guardrails Context",
    accessorKey: "guardrail_context_assessment",
  },
  {
    header: "Guardrails Model Response",
    accessorKey: "guardrail_result_assessment",
  },
]);

const items = ref([
  {
    label: "Question Metrics",
    slot: "account",
  },
  {
    label: "Details",
    slot: "details",
  },
  {
    label: "Breakdown",
    slot: "cost-breakdown",
  },
]);
</script>

<template>
  <div>
    <Breadcumb />
    <UTabs
      :items="items"
      :unmount-on-hide="false"
      class="w-full experiment-details-tabs"
      variant="pill"
    >
      <template #account="{ item }">
        <UCard>
          <template #header>
            <div class="flex justify-between items-center">
              <h2 class="text-xl font-medium">Experiment Question Metrics</h2>
              <DownloadResultsButton
                :results="questionMetrics?.question_metrics"
                button-label="Download Results"
                :question-metrics="true"
              />
            </div>
          </template>
          <UTable
            class="h-100 experiment-details-table"            
            sticky
            :columns="columns"
            :data="questionMetrics?.question_metrics"
            :loading="isLoading"
          >
           <template #empty>
            <div  class="flex flex-col items-center justify-center py-6">
              <p v-if="isLoading" class="text-gray-500">Please wait, we are fetching experiment question metrics...!</p>
              <p v-else>No valid experiments are found...!</p>
            </div>
          </template>
           <template #sno-cell="{ row }">
            <td>{{ row.index + 1 }}</td>
          </template>
            <template #guardrail_input_assessment-cell="{ row }">
              <template v-if="row.original.guardrail_input_assessment">
                <ProjectExperimentAssessments
                  :label="'Input Assessment'"
                  :assessments="row.original.guardrail_input_assessment"
                />
              </template>
              <template v-else> No Action Taken </template>
            </template>
            <template #guardrail_context_assessment-cell="{ row }">
              <template v-if="row.original.guardrail_context_assessment">
                <ProjectExperimentAssessments
                  :label="'Context Assessment'"
                  :assessments="row.original.guardrail_context_assessment"
                />
              </template>
              <template v-else> No Action Taken </template>
            </template>
            <template #guardrail_result_assessment-cell="{ row }">
              <template v-if="row.original.guardrail_output_assessment">
                <ProjectExperimentAssessments
                  :label="'Result Assessment'"
                  :assessments="row.original.guardrail_output_assessment"
                />
              </template>
              <template v-else> No Action Taken </template>
            </template>
          </UTable>
        </UCard>
      </template>
      <template #details="{ item }">
        <ProjectExperimentDetailsButton
          :experiments-data="experimentsData"
          :loading="isLoadingExperiments"
        />
      </template>
      <template #cost-breakdown="{ item }">
        <UCard class="my-5">
          <template #header>
            <h2 class="text-xl font-medium">Breakdown</h2>
          </template>
          <UCard class="my-5">
            <template #header>
              <h4 class="text-lg font-medium">Price</h4>
            </template>
            <table class="w-full">
              <tbody>
                <tr>
                  <td class="font-medium w-40">Indexing Cost</td>
                  <td class="w-40">
                    {{
                      experimentsData?.indexing_cost ?
                      useHumanCurrencyAmount(
                        experimentsData?.indexing_cost
                      ) : !experimentsData?.config?.bedrock_knowledge_base ? 'Unable to fetch data ' : 'Bedrock knowledge base pricing not included'
                    }}
                  </td>
                </tr>
                <tr>
                  <td class="font-medium">Retrieval Cost</td>
                  <td>
                    {{
                      experimentsData?.retrieval_cost ? 
                      useHumanCurrencyAmount(
                        experimentsData?.retrieval_cost
                      ) : 'Unable to fetch data'
                    }}
                  </td>
                </tr>
                <tr>
                  <td class="font-medium">Evaluation Cost</td>
                  <td>
                  
                    {{
                      experimentsData?.eval_cost ? 
                      useHumanCurrencyAmount(
                        experimentsData?.eval_cost
                      ) : 'Unable to fetch data'
                    }}
                  </td>
                </tr>
              </tbody>
            </table>
          </UCard>

          <UCard>
            <template #header>
              <h4 class="text-lg font-medium">Time</h4>
            </template>
            <table class="w-full text-left">
              <tbody>
                <tr>
                  <td class="font-medium w-40">Indexing Time</td>
                  <td class="w-40">
                    {{ 
                      experimentsData?.indexing_time ? 
                      useConvertSecondsToDHM(Number(experimentsData?.indexing_time)) 
                      : !experimentsData?.config?.bedrock_knowledge_base ? "Unable to fetch time" : 'NA'
                    }}
                  </td>
                </tr>
                <tr>
                  <td class="font-medium">Retrieval Time</td>
                  <td>
                    {{
                      experimentsData?.retrieval_time ? 
                      useConvertSecondsToDHM(Number(experimentsData?.retrieval_time))
                      : 'Unable to fetch time'
                    }}
                  </td>
                </tr>
                <tr>
                  <td class="font-medium">Evaluation Time</td>
                  <td >
                    {{ 
                      experimentsData?.eval_time ? 
                      useConvertSecondsToDHM(Number(experimentsData?.eval_time))
                      :'Unable to fetch time'
                    }}
                  </td>
                </tr>
              </tbody>
            </table>
          </UCard>

          <UCard class="my-4">
            <template #header>
              <h4 class="text-lg font-medium">Tokens</h4>
            </template>
            <table class="w-full">
              <tbody>
                <tr>
                  <td class="font-medium w-40">Indexing Embedded Tokens</td>
                  <td class="w-40">
                    {{ experimentsData?.index_embed_tokens }}
                  </td>
                </tr>
              </tbody>
            </table>
            <UCard class="my-4">
              <template #header>
                <h4 class="font-medium">
                  Total Tokens for
                  {{ questionMetrics?.question_metrics?.length }} Questions
                </h4>
              </template>
              <table class="w-full">
                <tbody>
                  <tr>
                    <td class="font-medium w-40">Retrieval Input Tokens</td>
                    <td class="w-40">{{ experimentsData?.retrieval_input_tokens }}</td>
                  </tr>
                  <tr>
                    <td class="font-medium">Retrieval Output Tokens</td>
                    <td>{{ experimentsData?.retrieval_output_tokens }}</td>
                  </tr>
                  <tr>
                    <td class="font-medium">Retrieval Query Embedded Tokens</td>
                    <td>{{ experimentsData?.retrieval_query_embed_tokens }}</td>
                  </tr>
                </tbody>
              </table>
            </UCard>
          </UCard>
        </UCard>
      </template>
    </UTabs>
  </div>
</template>
