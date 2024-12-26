<script setup lang="ts">
import { useMutation, useQuery } from "@tanstack/vue-query";

definePageMeta({
  hideInfraAlert: true,
});

const project = inject<Ref<Project>>("project");
const experimentError = ref("");
const loadValidExperiments = ref(false);
const isAllValidExperimentsFetched = ref(false);

/**
 * The below block will fetch valid-experiment status
 */
const { isSuccess: isExperimentFetchSuccess, isLoading: experimentLoading } =
  useQuery({
    queryKey: ["projects", project, "valid-experiments"],
    queryFn: async () => {
      try {
        const data = await useProjectValidExperiments(project!.value?.id);
        return data;
      } catch (error: any) {
        experimentError.value = error.message;
        const toast = useToast();
        toast.add({
          title: "Error : " + experimentError.value,
          color: "error",
          icon: "i-lucide-x-circle",
        });
        throw new Error(error.message);
      }
    },
    retry: false,
  });

// Start Polling for  Valid-experiments with interval 10 seconds
const { data: validExperiments } = useQuery<ValidExperiment[]>({
  queryKey: ["projects", project, "valid-experiments", "poll"],
  queryFn: async () => {
    try {
      loadValidExperiments.value = true;
      const response = await useProjectValidExperimentsByPoll(
        project!.value?.id
      );
      // The below 200 status represents completly fetch all valid experiments
      if (response.status === 200) {
        isAllValidExperimentsFetched.value = true;
        // 202 represents valid experiments pending
      } else if (response.status === 202) {
        return;
      }
      loadValidExperiments.value = false;
      return response._data;
    } catch (error: any) {
      const toast = useToast();
      toast.add({
        title: "Error : " + error.message,
        color: "error",
        icon: "i-lucide-x-circle",
      });
      isAllValidExperimentsFetched.value = true;
      loadValidExperiments.value = false;
      throw new Error("Error while fetching valid experiments : ", error);
    }
  },
  enabled: isExperimentFetchSuccess,
  refetchInterval: computed(() =>
    isAllValidExperimentsFetched.value ? false : 10000
  ),
  staleTime: Infinity,
  retry: false,
});

const { mutateAsync: createExperiments, isPending: isCreatingExperiments } =
  useMutation({
    mutationFn: (data: ValidExperiment[]) =>
      useProjectCreateExperiments(project!.value?.id, data),
  });

const selectedExperiments = ref<ValidExperiment[]>([]);
const handleReviewAndRun = async () => {
  await createExperiments(selectedExperiments.value);
  navigateTo({
    name: "projects-id-execute",
    params: {
      id: project!.value?.id,
    },
  });
};

const validExperimentsCount = computed(() => {
  return validExperiments?.value?.length;
});

useHead({
  title: "Valid Experiments",
});
</script>

<template>
  <div>
    <Breadcumb />
    <div
      v-if="experimentLoading && !experimentError"
      class="flex justify-center items-center h-24"
    >
      Experiments Verifying....
    </div>
    <UAlert
      v-else-if="experimentError && !experimentLoading"
      :description="experimentError"
      title="Error : "
    />
    <UCard v-else>
      <template #header>
        <h2 class="text-xl font-medium">
          Valid Experiments
          {{
            validExperimentsCount ? `(${validExperimentsCount} Identified)` : ""
          }}
        </h2>
      </template>
      <ProjectExperimentValidList
        v-model="selectedExperiments"
        selectable
        :experiments="validExperiments"
        :loading="loadValidExperiments"
      />
      <div class="flex justify-end mt-4">
        <div class="flex gap-2">
          <ProjectDownloadConfigButton
            v-if="selectedExperiments.length < 1"
            :project-id="project!.id"
            variant="outline"
          />
          <UButton
            icon="i-lucide-play"
            :disabled="selectedExperiments?.length === 0"
            :loading="isCreatingExperiments"
            @click="handleReviewAndRun"
          >
            Run ({{ selectedExperiments?.length || 0 }})
          </UButton>
        </div>
      </div>
    </UCard>
  </div>
</template>
