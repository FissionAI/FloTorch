<script setup lang="ts">

const isOpen = ref(false)
</script>



<template>
  <UButton icon="i-lucide-circle-help" color="neutral" variant="ghost" @click="isOpen = true" />
  <UModal class="primary-modal-with-header" v-model:open="isOpen" title="How to use prompt guide" description="&nbsp;">
    <template #body>
      <p class="font-medium">Your prompt guide must be a valid JSON file containing three key sections:</p>
      <ul class="ml-8 list-disc">
        <li>
          <span class="font-medium">System Prompt</span>: Instructions for the AI model
        </li>
        <li>
          <span class="font-medium">Base Prompt</span>: Template for your main prompt
        </li>
        <li>
          <span class="font-medium">Examples</span>: Collection of input/output pairs
        </li>
      </ul>
      <p class="mt-4 font-medium">Both the system prompt and user prompt are required</p>
      <p class="mt-4 font-medium">
        View <a href="/prompt-guide.json" target="_blank" class="underline font-medium hover:text-primary-600">sample
          prompt guide</a> to understand the correct format
      </p>
      <p class="mt-4 font-medium">When using N-shot prompting:</p>
      <ol class="ml-8 mt-1 list-disc text-gray-600">
        <li>Your guide must contain at least N example pairs</li>
        <li>Example: For 3-shot prompting, provide 3 or more examples</li>
        <li>FloTorch randomly selects N examples to enhance the prompt</li>
      </ol>
    </template>
    <template #footer>
      <div class="flex justify-end w-full">
        <UButton class="secondary-btn" @click="isOpen = false">Close</UButton>
      </div>
    </template>
  </UModal>
</template>
