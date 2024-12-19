<script setup lang="ts">

const modelValue = defineModel<string>()

const props = defineProps<{
  data: {
    path: string,
    presignedurl: string
  }
  accept?: string
}>()

const { open, reset, onChange } = useFileDialog({
  accept: props.accept || "*",
  directory: false,
})

const toast = useToast()
const filepath = ref(modelValue)
const isUploading = ref(false)
const error = ref<string | null>(null)

onChange(async (files) => {
  if (!files || files.length === 0) {
    return
  }
  const file = files[0]

  if (props.accept && file && !file.type.match(props.accept)) {
    error.value = `Please upload a ${props.accept} file`
    toast.add({
      title: 'Invalid file type',
      description: error.value,
      color: 'error'
    })
    reset()
    return
  }

  if (file && file.size > 40 * 1024 * 1024) {
    error.value = 'File size should not exceed 40MB'
    toast.add({
      title: 'File too large',
      description: error.value,
      color: 'error'
    })
    reset()
    return
  }

  if (props.accept && file && file.type.match("application/json")) {
    const text = await file.text()
    const json = JSON.parse(text)
    if (json&& json.length > 50) {
      error.value = 'Question numbers should not exceed 50'
      toast.add({
        title: 'Max 50 questions',
        description: error.value,
        color: 'error'
      })
      reset()
      return
    }
  }

  isUploading.value = true
  try {
    await $fetch(props.data.presignedurl, {
      method: "PUT",
      body: file
    })
    isUploading.value = false
    filepath.value = props.data.path
    modelValue.value = props.data.path
    toast.add({
      title: 'File Upload',
      description: 'File uploaded successfully',
      color: 'success'
    })
  } catch (error) {
    console.error(error)
    toast.add({
      title: 'Upload failed',
      description: 'There was an error uploading your file',
      color: 'error'
    })
  } finally {
    isUploading.value = false
  }
  reset()
})

</script>



<template>
  <UButtonGroup class="w-full">
    <UInput v-model="filepath" disabled />
    <UButton color="neutral" variant="subtle" icon="i-lucide-upload" :loading="isUploading" @click="open()" />
  </UButtonGroup>
</template>
