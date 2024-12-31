<script setup lang="ts">
import { useMutation, useQuery } from '@tanstack/vue-query';

definePageMeta({
  hideInfraAlert: true
})

const project = inject<Ref<Project>>("project")
const { data: validExperiments, isLoading } = useQuery({
  queryKey: ["projects", project, "valid-experiments"],
  queryFn: () => useProjectValidExperiments(project!.value?.id),
})

const { mutateAsync: createExperiments, isPending: isCreatingExperiments } = useMutation({
  mutationFn: (data: ValidExperiment[]) => useProjectCreateExperiments(project!.value?.id, data)
})

const selectedExperiments = ref<ValidExperiment[]>([])
const handleReviewAndRun = async () => {
  await createExperiments(selectedExperiments.value)
  navigateTo({
    name: "projects-id-execute",
    params: {
      id: project!.value?.id
    }
  })
}

const validExperimentsCount = computed(() => {
  return validExperiments?.value?.length
})


useHead({
  title: "Valid Experiments"
})
</script>



<template>
  <UCard>
    <template #header>
      <h2 class="text-xl font-medium">
        Valid Experiments {{ validExperimentsCount ? `(${validExperimentsCount} Identified)` : '' }}
      </h2>
    </template>
    <ProjectExperimentValidList v-model="selectedExperiments" selectable :experiments="validExperiments"
      :loading="isLoading" />
    <div class="flex justify-end mt-4">
      <div class="flex gap-2">
        <ProjectDownloadConfigButton v-if="selectedExperiments.length < 1" :project-id="project!.id"
          variant="outline" />
        <UButton icon="i-lucide-play" :disabled="selectedExperiments?.length === 0" :loading="isCreatingExperiments"
          @click="handleReviewAndRun">
          Run ({{ selectedExperiments?.length || 0 }})
        </UButton>
      </div>
    </div>
  </UCard>
</template>
