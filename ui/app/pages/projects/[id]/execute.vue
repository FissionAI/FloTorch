<script setup lang="ts">
import { useMutation, useQuery } from '@tanstack/vue-query';

definePageMeta({
  hideInfraAlert: true
})

const project = inject<Ref<Project>>("project")

const { data: experiments, isLoading } = useQuery({
  queryKey: ["projects", project, "experiments"],
  queryFn: () => useProjectExperiments(project!.value?.id),
})

const { mutateAsync: executeRun, isPending: isExecutingRun } = useMutation({
  mutationFn: () => useProjectExecute(project!.value?.id),
  onSuccess: () => {
    const toast = useToast()
    toast.add({
      title: "Run created",
      description: "Run created successfully",
      icon: "i-lucide-check"
    })
    // navigateTo({
    //   name: "index",
    // })
    window.location.href="/projects"
  }
})


const handleExecuteRun = async () => {
  await executeRun()
}

const validExperiments = computed(() => {
  return experiments.value?.map((experiment) => {
    return experiment.config as ValidExperiment
  }) || []
})

useHead({
  title: "Execute Run"
})
</script>

<template>
<Breadcumb />
  <UCard>
    <template #header>
      <h2 class="text-xl font-medium">Selected Experiments</h2>
    </template>
    <ProjectExperimentValidList :experiments="validExperiments" :loading="isLoading" />
    <div class="flex justify-end mt-4">
      <div class="flex justify-between gap-4">
        <UButton variant="outline" icon="i-lucide-x" @click="navigateTo({ name: 'projects-id-validexperiments' })">
          Cancel
        </UButton>
        <UButton icon="i-lucide-check" :loading="isExecutingRun" @click="handleExecuteRun">
          Confirm
        </UButton>
      </div>
    </div>
  </UCard>
</template>
