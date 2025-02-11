<script setup lang="ts">
useHead({
  titleTemplate(title) {
    return title ? `${title} | FloTorch` : "FloTorch"
  },
})
</script>

<template>
  <div class="flex flex-col min-h-screen bg-gray-100">
    <header class="bg-gray-800 text-white p-2 sticky top-0 z-50">
      <div class="container mx-auto flex justify-between items-center">
        <div>
          <NuxtLink :to="{ name: 'index' }">
            <img src="/logo.png" alt="logo" class="w-32" />
          </NuxtLink>
        </div>
        <UButton icon="i-lucide-github" variant="outline" color="neutral" href="https://github.com/FissionAI/FloTorch"
          target="_blank" />
      </div>
    </header>
    <main class="flex-1 container mx-auto py-4">
      <slot />
    </main>
    <footer class="bg-gray-800 text-white p-2 text-sm">
      <div class="container mx-auto flex justify-center items-center">
        <div>
          Powered by <a href="https://flotorch.ai?utm_source=flowtorch-repo" target="_blank"
            class="text-white underline">FloTorch.ai</a> For
          more information, contact us at <a href="mailto:info@flotorch.ai"
            class="text-white underline">info@flotorch.ai</a>
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
  padding: 50px !important;
}
</style>