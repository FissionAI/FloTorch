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
      class="w-full"
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
              />
            </div>
          </template>
          <UTable
            class="h-100"
            sticky
            :columns="columns"
            :data="questionMetrics?.question_metrics"
            :loading="isLoading"
          >
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
                  <td class="font-medium w-40">Indexing Cost Estimate</td>
                  <td class="w-40">
                    {{
                      experimentsData?.config?.indexing_cost_estimate ?
                      useHumanCurrencyAmount(
                        experimentsData?.config?.indexing_cost_estimate
                      ) : 'Unable to fetch data'
                    }}
                  </td>
                </tr>
                <tr>
                  <td class="font-medium">Retrieval Cost Estimate</td>
                  <td>
                    {{
                      experimentsData?.config?.retrieval_cost_estimate ? 
                      useHumanCurrencyAmount(
                        experimentsData?.config?.retrieval_cost_estimate
                      ) : 'Unable to fetch data'
                    }}
                  </td>
                </tr>
                <tr>
                  <td class="font-medium">Evaluation Cost Estimate</td>
                  <td>
                  
                    {{
                      experimentsData?.config?.eval_cost_estimate ? 
                      useHumanCurrencyAmount(
                        experimentsData?.config?.eval_cost_estimate
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
                      : 'Unable to fetch time'
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
