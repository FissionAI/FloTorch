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
          note: 'Drag and drop files/folders here'
        }"
      >
      </Dashboard>
      
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
      // required: true
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

  #radix-vue-dialog-content-v-0-15 div:first-child{
    border-bottom: none !important;
  }
  .uppy-DashboardContent-title {
    font-weight: 700 !important;
  }
    .uppy-DashboardContent-addMore {
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    display: none !important;
    }
    .uppy-Dashboard-AddFiles-title {
      display: none !important;
    }
    .uppy-Dashboard-AddFiles-info {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: 1.2em;
      font-weight: bold;
      margin: 15px 0;
      text-align: center;
    }

    .uppy-Dashboard--singleFile .uppy-Dashboard-filesInner {
      align-items: unset !important;
    }

    .uppy-Dashboard--singleFile .uppy-Dashboard-Item{
      height: 71px;
    }
    .uppy-Dashboard--singleFile .uppy-Dashboard-Item{
      flex-direction: row;
      padding: 0px !important;
    }

    .uppy-Dashboard--singleFile .uppy-Dashboard-Item-preview {
      width: 50px !important;
      height: 50px !important;
      margin-right: 12px !important;
      flex-shrink: unset !important;
      flex-grow: unset !important;
    }
    .uppy-Dashboard--singleFile.uppy-size--height-md .uppy-Dashboard-Item-action--remove {
      top: unset !important;
    }

    .uppy-StatusBar.is-waiting .uppy-StatusBar-actions button{
      background-color: var(--aws-primary-color) !important;
      color: var(--aws-font-grey-color) !important;
      border-radius: 0.25rem !important;
      border-color: var(--aws-primary-color) !important;
      border-end-start-radius: 20px !important;
      border-end-end-radius: 20px !important;
      border-start-start-radius: 20px !important;
      border-start-end-radius: 20px !important;
      font-weight: 700 !important;
      font-size: 14px !important;
      line-height: 22px !important;
      padding: 4px 20px !important;
      width: 35%;
      margin: 0 auto;
    }

    .uppy-u-reset.uppy-Dashboard-Item-action.uppy-Dashboard-Item-action--remove svg{
      height: 30px !important;
      width: 30px !important;
    }

    .uppy-u-reset.uppy-Dashboard-Item-action.uppy-Dashboard-Item-action--remove svg path:first-child{
      d: unset
    }

    .uppy-u-reset.uppy-Dashboard-Item-action.uppy-Dashboard-Item-action--remove svg path:last-child{
      fill: black !important;
    }

    /* .uppy-StatusBar.is-complete .uppy-StatusBar-progress {
      background-color: var(--aws-secondary-color) !important;
    } */
</style>
