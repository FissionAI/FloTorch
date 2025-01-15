<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query';


const props = defineProps<{
  projectId: string,
  disabled?: boolean
}>()

const { data: project, isLoading } = useQuery({
  queryKey: ["project", props.projectId],
  queryFn: () => useProject(props.projectId)
})

const config = computed(() => {
  return project.value?.config
})

const handleDownload = () => {
  const blob = new Blob([JSON.stringify(config.value)], { type: 'application/json' })
  const link = document.createElement("a");
  link.download = `${project.value?.id}_config.json`;
  link.href = URL.createObjectURL(blob)
  link.dataset.downloadurl = ["text/json", link.download, link.href].join(":");
  const evt = new MouseEvent("click", {
    view: window,
    bubbles: true,
    cancelable: true,
  });
  link.dispatchEvent(evt);
  link.remove()
}
</script>



<template>
  <UButton icon="i-lucide-download" label="Download Config" :loading="isLoading" :disabled="props.disabled" @click="handleDownload" />
</template>
