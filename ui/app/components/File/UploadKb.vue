<script setup lang="ts">

const modelValue = defineModel<string | string[]>()

const props = defineProps<{
//   data: {
//     path: string,
//     presignedurl: string
//   }
  accept?: string,
  fileUploadId?: string,
  kbFilesUploaded?: string[]
}>()

const emit = defineEmits(['kbFiles']);

const openModal = ref(false)

const openModalFunction = () => {
  openModal.value = true
}

const closeModal = () => {
  openModal.value = false
}

const filepath = ref<string | string[]>(modelValue)
const isUploading = ref(false)

const persistentFiles = ref([])
const onFileData = (data: any) => {
  persistentFiles.value = data.completedFiles
  emit('kbFiles', persistentFiles.value)
  filepath.value = data.uploadedFiles[0].name.split('/kb_data')[0]+'/kb_data'
}


</script>



<template>
  <UButtonGroup class="w-full">
    <UInput v-model="filepath" disabled />
    <UModal v-model:open="openModal" v-model:close="openModal" title="Upload KB data files">
      <UButton class="reduced-secondary-btn secondary-btn ml-2" leading-icon="i-lucide-arrow-up-to-line" label="Choose Files" variant="ghost" :loading="isUploading" @click="openModalFunction" />
      
      <template #body>
        <FileUploadModal 
          :file-upload-id="fileUploadId" 
          @file-data="onFileData" 
          @close-kb-upload-modal="closeModal" 
          :persistent-files="kbFilesUploaded || persistentFiles"
        />
      </template>
    </UModal>
  </UButtonGroup>
</template>
