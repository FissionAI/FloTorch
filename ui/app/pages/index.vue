<script setup lang="ts">

definePageMeta({
  layout: false
})

useHead({
  title: "FloTorch"
})
</script>

<template>
  <div class="flex flex-col min-h-screen bg-white">
    <header class="navbar text-white p-2">
      <div class="container mx-auto flex justify-between items-center">
        <div>
          <img src="/logo.png" alt="logo" class="w-[163px]" />
        </div>
        <UButton class="height-[32px]" icon="i-lucide-github" variant="outline" color="neutral" href="https://github.com/FissionAI/FloTorch"
          target="_blank" />
      </div>
    </header>
    <main class="flex-1 container mx-auto flex flex-col items-center justify-center gap-4">
      <h1 class="text-4xl font-bold">FloTorch</h1>
      <p class="text-lg">Manage and run your GenAI experiments at scale with ease</p>
      <img src="/flotorch-hero.gif" alt="hero" class="w-full max-w-7xl" />
      <UButton class="primary-btn" label="Get Started" trailing-icon="i-lucide-arrow-right" :to="{ name: 'projects' }"
        size="xl" />
    </main>
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
</style>