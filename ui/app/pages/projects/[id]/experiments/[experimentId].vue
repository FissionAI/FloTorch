<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
import { useQuery } from "@tanstack/vue-query";
const experimentId = useRouteParams<string>("experimentId");

const project = inject<Ref<Project>>("project")

const { data: questionMetrics, isLoading } = useQuery({
  queryKey: ["projects", project, "question-metrics"],
  queryFn: () =>
    useProjectExperimentQuestionMetrics(project!.value?.id, experimentId.value),
})

useHead({
  title: "Question Metrics"
})

const columns = ref<TableColumn<ExperimentQuestionMetric>[]>([
  {
    header: "Question",
    accessorKey: "question",
  },
  {
    header: "Ground Truth",
    accessorKey: "gt_answer"
  },
  {
    header: "Generated Answer",
    accessorKey: "generated_answer"
  }, 
  {
    header : "Input Assessment",
    accessorKey: "guardrail_input_assessment"
  },
  {
    header : "Context Assessment",
    accessorKey: "guardrail_context_assessment"
  },
  {
    header : "Result Assessment",
    accessorKey: "guardrail_result_assessment"
  }
])


</script>



<template>
  <div>
    <Breadcumb />
    <UCard>
      <template #header>
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-medium">Experiment Question Metrics</h2>
          <div>
            <ProjectExperimentDetailsButton
              :experiment-id="experimentId"
              :project-id="project!.id"
            />
          </div>
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
            <template v-if="row.original.guardrail_input_assessment" >
              <ProjectExperimentAssessments :label="'Input Assessment'" :assessments="row.original.guardrail_input_assessment" />
            </template>
            <template v-else>
              NA
            </template>
          </template>
        <template #guardrail_context_assessment-cell="{ row }">
            <template v-if="row.original.guardrail_context_assessment" >
              <ProjectExperimentAssessments :label="'Context Assessment'" :assessments="row.original.guardrail_context_assessment" />
            </template>
            <template v-else>
              NA
            </template>
        </template>
        <template #guardrail_result_assessment-cell="{ row }">
            <template v-if="row.original.guardrail_result_assessment" >
              <ProjectExperimentAssessments :label="'Result Assessment'" :assessments="row.original.guardrail_result_assessment" />
            </template>
            <template v-else>
              NA
            </template>
        </template>
        
      </UTable>
      <div class="flex justify-end">
        <DownloadResultsButton
          :results="questionMetrics?.question_metrics"
          button-label="Download Results"
        />
      </div>
      </UCard>
  </div>
</template>
