<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query';
const projectId = useRouteParams<string>("id");

const { data: project } = useQuery({
  queryKey: ["projects", projectId],
  queryFn: () => useProject(projectId.value)
})

provide("project", project)

const title = computed(() => project!.value?.name || `Project - ${projectId.value}`)

const description = computed(() => {
  const string = "Project Status: " + useHumanProjectStatus(project!.value?.status, "Loading...")
  return string
})

const route = useRoute()
const data = useState('experimentsData');

// const showSetupExperimentsButton = computed(() => project!.value?.status === "not_started" && route.name === "projects-id")

const { isInfraAlertHidden } = useInfraAlertState()

const handleAlertClose = () => {
  isInfraAlertHidden.value = true
}


const hideInfraAlert = computed(() => {
  if (isInfraAlertHidden.value) {
    return true
  }
  if (route.matched.some((route) => route.meta.hideInfraAlert)) {
    return true
  }
  return false
})
</script>



<template>
  <div>
    <div v-if="!hideInfraAlert" class="mb-4">
      <UAlert class="info-alert" variant="subtle" icon="i-lucide-info"  :close="{
        icon: 'i-lucide-x',
        color: 'var(--aws-info-alert-color)',
        onClick: () => {
          handleAlertClose()
        }
      }"
         >
        <template #description>
        <div class="w-full">
            <p>The infrastructure provisioned for FloTorch experiments has to be explicitly deprovisioned to avoid incurring continued AWS billing.</p>
            <div v-if="data && data.config" class="my-2">
                <div class="font-bold">OpenSearch: </div> 
                <p>3-node cluster with r7g.2xlarge.search instance type </p>
                <template v-if="data?.config?.embedding_service === 'sagemaker' || data?.config?.retrieval_service === 'sagemaker'">
                <div class="font-bold">SageMaker: </div>
                <p v-if="data?.config?.retrieval_service==='sagemaker'"> {{useGetModelData('retrieval',data?.config?.retrieval_model)?.model_name}} :  {{useGetModelData('retrieval',data?.config?.retrieval_model)?.type}} </p>
                <p v-if="data?.config?.embedding_service==='sagemaker'">{{useGetModelData('indexing',data?.config?.embedding_model)?.model_name}} :  {{useGetModelData('indexing',data?.config?.embedding_model)?.type}} </p>
                </template>
            </div>
            
            </div>
        </template>
        </UAlert>
    </div>
    <Page v-if="project" :title="title" :to="{ name: 'projects-id', params: { id: projectId } }"
      :description="description">
      <!-- <template #actions>
        <UButton v-if="showSetupExperimentsButton" :to="{
          name: 'projects-id-validexperiments',
          params: {
            id: projectId
          }
        }" icon="i-lucide-play" label="Execute Run" />
      </template> -->
      <NuxtPage />
    </Page>
  </div>
</template>
