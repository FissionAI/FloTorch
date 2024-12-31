<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui';
import { useQuery, useMutation } from '@tanstack/vue-query';


const modelValue = defineModel<ProjectCreateDataStrategy>({
  default: () => {
    return {}
  }
})

// const { data: presignedUploadUrl } = useQuery({
//   queryKey: ["presignedUploadUrl"],
//   queryFn: () => usePresignedUploadUrl(),
// })

const presignedUploadUrl = ref()

const { mutateAsync: getPresignedUploadUrl, isPending: isFetchingPresignedUploadUrl } = useMutation({
  mutationFn: async (uuid: string) => {
    const response = await usePresignedUploadUrl(uuid)
    presignedUploadUrl.value = response
    return response
  }
})

onMounted(() => {
  getPresignedUploadUrl(props.fileUploadId as string)
})

const props = withDefaults(defineProps<{
  showBackButton?: boolean,
  nextButtonLabel?: string,
  fileUploadId?: string,
  kbFilesUploadedData?: string[],
}>(), {
  showBackButton: true,
  nextButtonLabel: "Next"
})

const kb_data_uploadedFiles = ref();
const fetchKbFiles = (files: String[]) => {
  kb_data_uploadedFiles.value = files
  emits('kbFilesUpload', files);
}

const state = reactive<Partial<ProjectCreateDataStrategy>>({
  name: modelValue.value?.name || undefined,
  region: modelValue.value?.region || undefined,
  kb_data: modelValue.value?.kb_data || undefined,
  gt_data: modelValue.value?.gt_data || undefined,
  // kb_data_uploadedFiles: modelValue.value?.kb_data_uploadedFiles || undefined,
})

const emits = defineEmits(["next", "previous", "kbFilesUpload"])

const onSubmit = (event: FormSubmitEvent<ProjectCreateDataStrategy>) => {
  modelValue.value = event.data
  emits("next")
}
</script>



<template>
  <UForm :schema="ProjectCreateDataStrategySchema" :state="state" :validate-on="['input']" @submit="onSubmit">
    <UFormField id="name" name="name" label="Project Name" required>
      <UInput v-model="state.name" type="text" />
      <template #hint>
        <FieldTooltip field-name="name" />
      </template>
    </UFormField>
    <UFormField id="region" name="region" label="Region" required>
      <RegionSelect v-model="state.region" />
      <template #hint>
        <FieldTooltip field-name="region" />
      </template>
    </UFormField>
    <UFormField id="kb_data" name="kb_data" label="Knowledge Base Data" required>
      <!-- <FileUploadModal v-if="presignedUploadUrl?.kb_data" key="kb_data" v-model="state.kb_data" accept="application/pdf" :data="presignedUploadUrl.kb_data"/> -->
      <FileUploadKb @kbFiles="fetchKbFiles" :kbFilesUploaded="props.kbFilesUploadedData" :file-upload-id="fileUploadId" key="kb_data" v-model="state.kb_data" accept="application/pdf" />
      <template #hint>
        <FieldTooltip field-name="kb_data" />
      </template>
    </UFormField>
    <UFormField id="gt_data" name="gt_data" label="Ground Truth Data" required>
      <FileUpload v-if="presignedUploadUrl?.gt_data" key="gt_data" v-model="state.gt_data" accept="application/json"
        :data="presignedUploadUrl.gt_data" />
      <template #hint>
        <FieldTooltip field-name="gt_data" />
      </template>
    </UFormField>
    <div class="flex justify-between items-center w-full mt-6">
      <div>
        <UButton v-if="showBackButton" type="button" icon="i-lucide-arrow-left" label="Back" variant="outline"
          @click.prevent="emits('previous')" />
      </div>
      <div>
        <UButton trailing-icon="i-lucide-arrow-right" :label="nextButtonLabel" type="submit" />
      </div>
    </div>
  </UForm>
</template>
