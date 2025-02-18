<script setup lang="ts">
const { $on } = useNuxtApp();

useHead({
  titleTemplate(title) {
    return title ? `${title} | FloTorch` : "FloTorch";
  },
});

const drawerOpen = ref(false);

const tooltip = ref("");
const fieldName = ref("");
const content = ref({});
$on("showTooltip", (tooltipInfo) => {
  drawerOpen.value = true;
  tooltip.value = tooltipInfo.tooltip.value;
  fieldName.value = tooltipInfo.fieldName;
  content.value = tooltipInfo.tooltip.value;
});
$on("closeTooltip", () => {
  drawerOpen.value = false;
});
const sharedData = ref({});

provide("sharedData", sharedData);


const router = useRouter()

// Listen for route changes after navigation
router.afterEach(() => drawerOpen.value = false)

</script>

<template>
  <div class="flex flex-col min-h-screen bg-white">
    <header class="navbar text-white p-2 sticky top-0 z-50 -mb-12">
      <div class="mx-10  flex flex-col">
        <div class="w-full flex justify-between">
          <NuxtLink :to="{ name: 'index' }" class="self-center">
            <img src="/logo.png" alt="logo" class="w-[200px]" />
          </NuxtLink>
          <UButton
            class="height-[32px] github-link self-center"
            icon="i-lucide-github"
            variant="outline"
            color="neutral"
            href="https://github.com/FissionAI/FloTorch"
            target="_blank"
          />
        </div>
        <Page
          class="my-30"
          :title="sharedData?.title"
          :to="sharedData?.to"
          :description="sharedData?.description"
          hide-slot="true"
        />
      </div>
    </header>
    <main
      class="w-full flex justify-between mx-auto py-4 w-full flex-1 container mx-auto py-4"
    >
      <div
        class="slot-div"
        :class="{ 'w-[78%]': drawerOpen, 'w-full': !drawerOpen }"
      >
        <div class="w-full">
          <slot />
        </div>
      </div>
      <UCard
        class="drawer-content  -mr-10"
        :class="{ 'w-[20%] h-auto': drawerOpen, hidden: !drawerOpen }"
      >
      <template #header>
      <div class="w-full flex justify-between">
              <h1 class="tooltip-title pr-[8px]">{{ tooltip?.label?.charAt(0).toUpperCase() + tooltip?.label?.slice(1) }}</h1>
      
          <UButton class="cursor-pointer" icon="i-lucide-chevron-right" variant="ghost" color="primary-gray " @click.prevent="drawerOpen=false" />
        </div>
      </template>
        <template #default>
        
          <div class=" h-[calc(100% - 66px)]">
            <Placeholder class="">
              <div class="tooltip-description pr-[8px]" v-html="content?.info"></div>
              <div v-if="content.link" class="tooltip-description mt-3 pr-[8px]"> 
                <div v-if="content.label !== 'Service'">
                  <h4 class="text-[18px] font-bold">Learn More <UIcon name="i-rivet-icons:link-external"/></h4>
              <ul class="my-4">
              <li>
               <NuxtLink target="_blank" :to="`https://github.com/FissionAI/FloTorch/blob/v2.1.0/Help_Links.MD#${content.link}`" class="font-bold py-5 external-link">{{content.label}}</NuxtLink>

              </li>
              <!-- <li v-else>
                <NuxtLink target="_blank" :to="`https://github.com/FissionAI/FloTorch/blob/v2.1.0/Help_Links.MD`" class="font-bold py-5 external-link">Documentation</NuxtLink>
              </li> -->
              </ul>
                </div>
                <div v-else-if="content.label === 'Service'">
                  <h4 class="text-[18px] font-bold">Learn More <UIcon name="i-rivet-icons:link-external"/></h4>
                  <ul class="my-4">
                  <li v-for="link in content.link" :key="link.label">
                    <NuxtLink target="_blank" :to="link.link" class="font-bold py-5 external-link">{{link.label}}</NuxtLink>
                  </li>
                  </ul>
                </div>
              </div>
            </Placeholder>
          </div>
          </template>
      </UCard>
    </main>

    <footer class="navbar w-full text-white p-2 text-sm z-100">
      <div class="container mx-auto flex justify-center items-center">
        <div>
          Powered by
          <a
            href="https://flotorch.ai?utm_source=flowtorch-repo"
            target="_blank"
            class="external-link"
            >FloTorch.ai<UIcon class="ml-[5px]" name="i-rivet-icons:link-external"
          /></a>
          For more information, contact us at
          <a href="mailto:info@flotorch.ai" class="external-link"
            >info@flotorch.ai<UIcon class="ml-[5px]" name="i-rivet-icons:link-external" /></a
          >
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
  padding-bottom:0px !important;
}

.drawer-content {
  position: fixed;
  height: 87%;
  right: 40px;
  overflow-y: scroll;
}
</style>
