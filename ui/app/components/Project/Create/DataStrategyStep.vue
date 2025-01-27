<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui";
import { useQuery, useMutation } from "@tanstack/vue-query";

const modelValue = defineModel<ProjectCreateDataStrategy>({
  default: () => {
    return {};
  },
});

// const { data: presignedUploadUrl } = useQuery({
//   queryKey: ["presignedUploadUrl"],
//   queryFn: () => usePresignedUploadUrl(),
// })

const presignedUploadUrl = ref();

const {
  mutateAsync: getPresignedUploadUrl,
  isPending: isFetchingPresignedUploadUrl,
} = useMutation({
  mutationFn: async (uuid: string) => {
    const response = await usePresignedUploadUrl(uuid);
    presignedUploadUrl.value = response;
    return response;
  },
});

onMounted(() => {
  getPresignedUploadUrl(props.fileUploadId as string);
});

const props = withDefaults(
  defineProps<{
    showBackButton?: boolean;
    nextButtonLabel?: string;
    fileUploadId?: string;
    kbFilesUploadedData?: string[];
  }>(),
  {
    showBackButton: true,
    nextButtonLabel: "Next",
  }
);

const kb_data_uploadedFiles = ref();
const fetchKbFiles = (files: String[]) => {
  kb_data_uploadedFiles.value = files;
  emits("kbFilesUpload", files);
};

const state = reactive<Partial<ProjectCreateDataStrategy>>({
  name: modelValue.value?.name || undefined,
  region: modelValue.value?.region || undefined,
  kb_model: modelValue.value?.kb_model || undefined,
  kb_data: modelValue.value?.kb_data || undefined,
  gt_data: modelValue.value?.gt_data || undefined,
  // kb_data_uploadedFiles: modelValue.value?.kb_data_uploadedFiles || undefined,
});

const emits = defineEmits(["next", "previous", "kbFilesUpload"]);

const onSubmit = (event: FormSubmitEvent<ProjectCreateDataStrategy>) => {
    modelValue.value = event.data;
  emits("next");
};

const meta = useKnowledgeBaseModel();

const updateKbModels = (event: any) => {
  state.kb_data = event.value;
};

const resetKbModel = (event: any) => {
  state.kb_data = [];
};
</script>

<template>
  <UForm
    :schema="ProjectCreateDataStrategySchema"
    :state="state"
    :validate-on="['input']"
    @submit="onSubmit"
  >
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

    <UFormField
      id="kb_model"
      name="kb_model"
      label="Select Knowledge Base Type"
      required
    >
      <USelectMenu
        :items="meta.kb_model"
        v-model="state.kb_model"
        class="w-full"
        value-key="value"
        @change="resetKbModel"
        
      />
      <template #hint>
        <FieldTooltip field-name="kb_model" />
      </template>
       <div class="my-2">
          <ULink class="text-blue-500 hover:underline" target="_blank" raw :to="`https://${state.region}.console.aws.amazon.com/bedrock/home?region=${state.region}#/knowledge-bases`" active-class="font-bold" inactive-class="text-[var(--ui-text-muted)]">Create Bedrock knowdege bases</ULink>
        </div>
    </UFormField>
      <p v-if="state.kb_model && state.kb_model !== 'default-upload'" class="text-blue-500">[Note]: Indexing Strategy step will be skipped if Bedrock Knowledge Bases is selected </p>

    <template v-if="state.kb_model && state.kb_model === 'default-upload'">
      <UFormField
        id="kb_data"
        name="kb_data"
        label="Knowledge Base Data"
        required
      >
        <FileUploadKb
          @kbFiles="fetchKbFiles"
          :kbFilesUploaded="props.kbFilesUploadedData"
          :file-upload-id="fileUploadId"
          key="kb_data"
          v-model="state.kb_data"
          accept="application/pdf"
        /> 
      </UFormField>
    </template>
    <template v-if="state.kb_model && state.kb_model !== 'default-upload'">
        <FetchKbModels
          @kbModels="updateKbModels"
          v-model="state.kb_data"
          key="kb_data"
          :selectedValue="state.kb_data"
          :region="state.region"
        />

    </template>
    <UFormField id="gt_data" name="gt_data" label="Ground Truth Data" required>
      <FileUpload
        v-if="presignedUploadUrl?.gt_data"
        key="gt_data"
        v-model="state.gt_data"
        accept="application/json"
        :data="presignedUploadUrl.gt_data"
      />
      <template #hint>
        <FieldTooltip field-name="gt_data" />
      </template>
    </UFormField>
    <div class="flex justify-between items-center w-full mt-6">
      <div>
        <UButton
          v-if="showBackButton"
          type="button"
          icon="i-lucide-arrow-left"
          label="Back"
          variant="outline"
          @click.prevent="emits('previous')"
        />
      </div>
      <div>
        <UButton
          trailing-icon="i-lucide-arrow-right"
          :label="nextButtonLabel"
          type="submit"
        />
      </div>
    </div>
  </UForm>
</template>
