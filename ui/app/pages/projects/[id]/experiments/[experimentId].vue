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
  }
])


</script>



<template>
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
      sticky
      :columns="columns"
      :data="questionMetrics?.question_metrics"
      :loading="isLoading"
    />
    <div class="flex justify-end">
      <DownloadResultsButton
        :results="questionMetrics?.question_metrics"
        button-label="Download Results"
      />
    </div>
  </UCard>
</template>
