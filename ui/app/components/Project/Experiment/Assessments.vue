<script setup lang="ts">

    const props = defineProps<{
    label : string
    assessments : any
    }>()
    
    const isOpen = ref(false)

</script>


<template>
  <a href="#" class="text-blue-500 hover:underline" @click.prevent="isOpen = true">View</a>
  <UModal class="overflow-y-scroll max-h-[50vh]" v-model:open="isOpen" :title="props.label">
    <template #body>
      <div class="w-full">
      {{JSON.parse(JSON.stringify(props.assessments))}}
      </div>
    </template>
  </UModal>
</template>