<script setup lang="ts">
const { $on } = useNuxtApp()

useHead({
  titleTemplate(title) {
    return title ? `${title} | FloTorch` : "FloTorch"
  },
})

const drawerOpen = ref(false)

const tooltip = ref('')
const fieldName = ref('')
$on('showTooltip', (tooltipInfo) => {
  console.log(tooltipInfo)
  drawerOpen.value = true
  tooltip.value = tooltipInfo.tooltip.value
  fieldName.value = tooltipInfo.fieldName
})
const sharedData = ref({})

provide('sharedData', sharedData)

</script>

<template>
  <div class="flex flex-col min-h-screen bg-gray-100">
    <header class="navbar text-white p-2 sticky top-0 z-50">
      <div class="mx-10 flex flex-col">
        <div class="w-full flex justify-between">
          <NuxtLink :to="{ name: 'index' }">
            <img src="/logo.png" alt="logo" class="w-32" />
          </NuxtLink>
        <UButton icon="i-lucide-github" variant="outline" color="neutral" href="https://github.com/FissionAI/FloTorch"
          target="_blank" />
        </div>
        <Page class="my-20" :title="sharedData.title" :to="sharedData.to"
      :description="sharedData.description" hide-slot="true"/>
      </div>
    </header>
    <main :class="{ 'pl-4 !pr-[calc(100vw-79%)]': drawerOpen, '': !drawerOpen }" class="flex-1 container mx-auto py-4">
      <slot />
    </main>
    <UDrawer v-model:open="drawerOpen" height="100" :handle="false" class="drawer-content" direction="right" :overlay="false">
        <template #content>
          <div class="w-96 h-[calc(100% - 66px)]">
            <Placeholder class="m-4">
              
              <h1 class="tooltip-title pr-[8px]">{{ fieldName.charAt(0).toUpperCase() + fieldName.slice(1) }}</h1>

              <p class="tooltip-description mt-7 pr-[8px]">{{ tooltip }}</p>
            </Placeholder>
          </div>
        </template>
  </UDrawer>
    <footer class="navbar text-white p-2 text-sm">
      <div class="container mx-auto flex justify-center items-center">
        <div>
          Powered by <a href="https://flotorch.ai?utm_source=flowtorch-repo" target="_blank"
            class="external-link">FloTorch.ai<UIcon name="i-rivet-icons:link-external" /></a> For
          more information, contact us at <a href="mailto:info@flotorch.ai"
            class="external-link">info@flotorch.ai<UIcon name="i-rivet-icons:link-external" /></a>.
        </div>
      </div>
    </footer>
  </div>
</template>


<style>

main.container {
  width: 100% !important;
  max-width: unset !important;
  min-width: unset !important;
  padding: 50px;
}

.drawer-content {
  height: calc(100% - 95px) !important;
    top: 58px;
    right: 0px;
}

</style>