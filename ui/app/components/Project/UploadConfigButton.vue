<script setup lang="ts">

const toast = useToast()
const { open, reset, onChange } = useFileDialog({
  accept: "application/json",
  directory: false
})

const openDialog = () => {
  open()
}

const { createConfig } = useProjectUploadConfig()

onChange((files) => {
  if (!files || files.length === 0) {
    return
  }
  const file = files[0]
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const json = JSON.parse(e.target?.result as string)
      const configId = createConfig(json)
      navigateTo({
        name: "projects-create",
        query: {
          configId
        }
      })
    } catch (error) {
      console.error(error)
      toast.add({
        title: 'Invalid config file',
        description: 'Please upload a valid config file',
        color: 'error'
      })
    }
  }
  reader.readAsText(file!, 'utf-8')
  reset()
})
</script>



<template>
  <UButton class="primary-btn" icon="i-lucide-upload" label="Upload Config" @click="openDialog" />
</template>