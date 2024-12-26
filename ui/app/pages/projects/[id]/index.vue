<script setup lang="ts">
import { useQuery } from "@tanstack/vue-query";

const project = inject<Ref<Project>>("project");
const projectId = computed(() => project!.value?.id);

if (project?.value?.status === "not_started") {
  navigateTo({
    name: "projects-id-validexperiments",
    params: {
      id: projectId.value,
    },
  });
}

watchEffect(() => {
  if (project?.value?.status === "not_started") {
    navigateTo({
      name: "projects-id-validexperiments",
      params: {
        id: projectId.value,
      },
    });
  }
});

const { data: experiments, isLoading } = useQuery({
  queryKey: ["projects", projectId, "experiments"],
  queryFn: () => useProjectExperiments(projectId.value),
  refetchInterval: () => {
    return 10000
  }
})

</script>



<template>
  <Breadcumb />
  <UCard v-if="project?.status !== 'not_started'">
    <template #header>
      <h2 class="text-xl font-medium">Running Experiments</h2>
    </template>
    <div v-if="isLoading" class="flex justify-center items-center h-24">
      Loading experiments...
    </div>
    <ProjectExperimentList
      v-else-if="experiments && experiments.length > 0"
      :experiments="experiments"
      :project-id="projectId"
    />
    <div v-else class="flex justify-center items-center h-24">
      No experiments found
    </div>
  </UCard>
  <UCard v-else>
    <div class="text-center">
      Please wait while we redirect you to setup experiments
    </div>
  </UCard>
</template>
