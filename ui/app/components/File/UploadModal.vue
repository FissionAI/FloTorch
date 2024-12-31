<template>
    <div id="FileUploadModal">
      <Dashboard
        :open="true"
        :uppy="uppy"
        :props="{
          proudlyDisplayPoweredByUppy: false,
          doneButtonHandler: () => {
            emit('close-kb-upload-modal');
          },
          fileManagerSelectionType: 'both',
        }"
      />
    </div>
  </template>
  
  <script setup>
  import { useMutation } from '@tanstack/vue-query'
  import { Dashboard } from '@uppy/vue'
  import Uppy from '@uppy/core'
  import AwsS3 from "@uppy/aws-s3";


  const props = defineProps({
    presignedUploadUrlData: {
      type: Object,
      required: true
    },
    fileUploadId: {
      type: String,
    },
    persistentFiles: {
      type: Array,
      required: true
    }
  })

  const emit = defineEmits(['file-data', 'close-kb-upload-modal'])
  const uploadedFiles = ref([])

  watch(() => props.persistentFiles, (newVal) => {
    console.log(newVal)
    
  })

const handleFetchKbPresignedUrls = async (unique_id, fileNames) => {
  await getKbPresignedUrls(fileNames)
}

const preSignedUrls = ref([])
const { mutateAsync: getKbPresignedUrls, isPending: isFetchingKbPresignedUrls } = useMutation({
  mutationFn: async (fileNames) => {
    const response = await usePresignedUploadUrlKb(props.fileUploadId, fileNames)
    preSignedUrls.value = response.files
    return response
  }
})

  onMounted(() => {
    props.persistentFiles.forEach(file => {
      uppy.addFile(file)
    })
  })

  const uppy = new Uppy({
    restrictions: {
      allowedFileTypes: ['application/pdf'],
      maxTotalFileSize: 100 * 1024 * 1024, // 100MB
    },
  })



  uppy.on('upload', async (uploadId, file) => {
    const filesToBeUploaded = completedFiles.value.map((file) => file.name)
    file.map((file) => {
        // const slug = props.fileUploadId+ '/'+'kb_data/' + useFileSlugifyOperation(file)
        // console.log(slug)
        filesToBeUploaded.push(useFileSlugifyOperation(file))
    })
    handleFetchKbPresignedUrls(props.fileUploadId, filesToBeUploaded)
  }).use(AwsS3, {
    companionUrl: null,
    async getUploadParameters(file) {
      while (isFetchingKbPresignedUrls.value) {
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      
      const filePresignedData = preSignedUrls.value.find(
        (urlData) => urlData.path.split('/')[5] === useFileSlugifyOperation(file)
      )

      if (!filePresignedData) {
        throw new Error('No presigned URL found for file')
      }

      return {
        method: 'PUT',
        url: filePresignedData.presignedurl,
        headers: {
          'Content-Type': file.type
        }
      }
    }
  })

  const completedFiles = ref([])
  uppy.on('complete', (result) => {
        completedFiles.value = result.successful;
        uploadedFiles.value = preSignedUrls.value.map((url) => ({
            uploadURL: url.presignedurl,
            name: url.path
        }))
        emit('file-data', {uploadedFiles: uploadedFiles.value, completedFiles: completedFiles.value});
    });

  </script>
  
  <style src="@uppy/core/dist/style.css"></style>
  <style src="@uppy/dashboard/dist/style.css"></style>
  <style src="@uppy/drag-drop/dist/style.css"></style>
  <style src="@uppy/progress-bar/dist/style.css"></style>
  <style>
    .uppy-DashboardContent-addMore {
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    display: none !important;
    }
</style>