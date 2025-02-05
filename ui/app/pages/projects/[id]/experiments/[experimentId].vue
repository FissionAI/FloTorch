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

const overall_metadata = computed(() => {
  return experimentsData.value.overall_metadata;
})

const indexing_metadata = computed(() => {
  return experimentsData.value.indexing_metadata;
})

const retriever_metadata = computed(() => {
  return experimentsData.value.retriever_metadata;
})

const inferencer_metadata = computed(() => {
  return experimentsData.value.inferencer_metadata;
})

const evaluation_metadata = computed(() => {
  return experimentsData.value.eval_metadata;
})

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
              <h4 class="text-lg font-medium">Overall</h4>
            </template>
            <table class="w-full">
              <tbody>
                <tr v-if="overall_metadata">
                  <td colspan="2">
                    <table class="w-full">
                      <tbody>
                        <tr v-for="(value, key) in overall_metadata" :key="key">
                          <td class="font-medium w-40">{{ key.split('_').join(' ').replace(/\w\S*/g, (w) => (w.replace(/^\w/, (c) => c.toUpperCase()))) }}</td>
                          <td v-if="key.includes('time')" class="w-40">{{ useConvertSecondsToDHM(Number(value)) }}</td>
                          <td v-else-if="key.includes('cost')" class="w-40">{{ useHumanCurrencyAmount(Number(value)) }}</td>
                          <td v-else class="w-40">{{ value }}</td> 
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>
              </tbody>
            </table>
          </UCard>
          <UCard class="my-5">
            <template #header>
              <h4 class="text-lg font-medium">Indexing</h4>
            </template>
            <table class="w-full">
              <tbody>
                <tr v-if="indexing_metadata">
                  <td colspan="2">
                    <table class="w-full">
                      <tbody>
                        <tr v-for="(value, key) in indexing_metadata" :key="key">
                          <td class="font-medium w-40">{{ key.split('_').join(' ').replace(/\w\S*/g, (w) => (w.replace(/^\w/, (c) => c.toUpperCase()))) }}</td>
                          <td v-if="key.includes('time')" class="w-40">{{ useConvertSecondsToDHM(Number(value)) }}</td>
                          <td v-else-if="key.includes('cost')" class="w-40">{{ useHumanCurrencyAmount(Number(value)) }}</td>
                          <td v-else class="w-40">{{ value }}</td> 
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>
              </tbody>
            </table>
          </UCard>

          <UCard class="my-5">
            <template #header>
              <h4 class="text-lg font-medium">Retrieval</h4>
            </template>
            <table class="w-full text-left">
              <tbody>
                <tr v-if="retriever_metadata">
                  <td colspan="2">
                    <table class="w-full">
                      <tbody>
                        <tr v-for="(value, key) in retriever_metadata" :key="key">
                          <td class="font-medium w-40">{{ key.split('_').join(' ').replace(/\w\S*/g, (w) => (w.replace(/^\w/, (c) => c.toUpperCase()))) }}</td>
                          <td v-if="key.includes('time')" class="w-40">{{ useConvertSecondsToDHM(Number(value)) }}</td>
                          <td v-else-if="key.includes('cost')" class="w-40">{{ useHumanCurrencyAmount(Number(value)) }}</td>
                          <td v-else class="w-40">{{ value }}</td> 
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>
              </tbody>
            </table>
          </UCard>

          <UCard class="my-5">
            <template #header>
              <h4 class="text-lg font-medium">Evaluation</h4>
            </template>
            <table class="w-full text-left">
              <tbody>
                <tr v-if="evaluation_metadata">
                  <td colspan="2">
                    <table class="w-full">
                      <tbody>
                        <tr v-for="(value, key) in evaluation_metadata" :key="key">
                          <td class="font-medium w-40">{{ key.split('_').join(' ').replace(/\w\S*/g, (w) => (w.replace(/^\w/, (c) => c.toUpperCase()))) }}</td>
                          <td v-if="key.includes('time')" class="w-40">{{ useConvertSecondsToDHM(Number(value)) }}</td>
                          <td v-else-if="key.includes('cost')" class="w-40">{{ useHumanCurrencyAmount(Number(value)) }}</td>
                          <td v-else class="w-40">{{ value }}</td> 
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>
              </tbody>
            </table>
          </UCard>

          <UCard class="my-5">
            <template #header>
              <h4 class="text-lg font-medium">Inferencer</h4>
            </template>
            <table class="w-full text-left">
              <tbody>
                <tr v-if="inferencer_metadata">
                  <td colspan="2">
                    <table class="w-full">
                      <tbody>
                        <tr v-for="(value, key) in inferencer_metadata" :key="key">
                          <td class="font-medium w-40">{{ key.split('_').join(' ').replace(/\w\S*/g, (w) => (w.replace(/^\w/, (c) => c.toUpperCase()))) }}</td>
                          <td v-if="key.includes('time')" class="w-40">{{ useConvertSecondsToDHM(Number(value)) }}</td>
                          <td v-else-if="key.includes('cost')" class="w-40">{{ useHumanCurrencyAmount(Number(value)) }}</td>
                          <td v-else class="w-40">{{ value }}</td> 
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>
              </tbody>
            </table>
          </UCard>

          <UCard class="my-5">
            <template #header>
              <h4 class="text-lg font-medium">Evaluation</h4>
            </template>
            <table class="w-full text-left">
              <tbody>
                <tr v-if="evaluation_metadata">
                  <td colspan="2">
                    <table class="w-full">
                      <tbody>
                        <tr v-for="(value, key) in evaluation_metadata" :key="key">
                          <td class="font-medium w-40">{{ key.split('_').join(' ').replace(/\w\S*/g, (w) => (w.replace(/^\w/, (c) => c.toUpperCase()))) }}</td>
                          <td v-if="key.includes('time')" class="w-40">{{ useConvertSecondsToDHM(Number(value)) }}</td>
                          <td v-else-if="key.includes('cost')" class="w-40">{{ useHumanCurrencyAmount(Number(value)) }}</td>
                          <td v-else class="w-40">{{ value }}</td> 
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>
              </tbody>
            </table>
          </UCard>
        </UCard>
      </template>
    </UTabs>
  </div>
</template>
