<script setup lang="ts">
useHead({
  title: "Create Project"
})

const configId = useRouteQuery<string>("configId")

const { getConfig } = useProjectUploadConfig()

const config = computed(() => getConfig(configId.value))
const sharedData = inject('sharedData')

onMounted(() => {
  sharedData.value.title = 'Create Project'
});

</script>

<template>
  <Page title="Create Project">
    <Breadcumb />
    <UCard>
      <div class="max-w-2xl mx-auto">
        <ProjectCreateForm :config="config" />
      </div>
    </UCard>
  </Page>
</template>
