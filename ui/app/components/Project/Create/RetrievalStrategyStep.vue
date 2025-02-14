<script setup lang="ts">
import type { FormError, FormSubmitEvent } from '@nuxt/ui';
import { useMax } from '@vueuse/math'


const props = withDefaults(defineProps<{
  showBackButton?: boolean,
  nextButtonLabel?: string,
  region?: string,
  kbModel:string | string[]
}>(), {
  showBackButton: true,
  nextButtonLabel: "Next",

})

const emits = defineEmits(['previous', 'next'])
const errorMsg = ref("");

const modelValue = defineModel<ProjectCreateRetrievalStrategy>({
  default: () => {
    return {}
  }
})

const state = reactive<ProjectCreateRetrievalStrategy>({
  knn_num: props.kbModel === 'none' ? [0] : (modelValue.value.knn_num || undefined),
  retrieval: modelValue.value.retrieval || undefined,
  n_shot_prompts: modelValue.value.n_shot_prompts || undefined,
  n_shot_prompt_guide: modelValue.value.n_shot_prompt_guide || undefined,
  temp_retrieval_llm: modelValue.value.temp_retrieval_llm || undefined,
  rerank_model_id: props.region === 'us-east-1' ? ['none'] : modelValue.value.rerank_model_id || undefined,
  // region: modelValue.value.region || props.region
})

const onSubmit = (event: FormSubmitEvent<ProjectCreateRetrievalStrategy>) => {
  modelValue.value = event.data
  emits('next')
}
const meta = useProjectCreateMeta()


const selectedMaxShotPrompts = computed(() => {
  return useMax(state.n_shot_prompts || [0]).value
})

const retForm = useTemplateRef("retForm")

const handlePromptGuideError = (error?: FormError) => {
  if (error) {
    errorMsg.value = error.message
    retForm.value?.setErrors([error])
  } else {
    errorMsg.value = ""
    retForm.value?.clear("n_shot_prompt_guide")
    // retForm.value?.setErrors([])
  }
}

const tooltip = ref('')
const fieldName = ref('')

const handleTooltip = (tooltipInfo: {tooltip: string, fieldName: string}) => {
  console.log(tooltipInfo)
  tooltip.value = tooltipInfo.tooltip
  fieldName.value = tooltipInfo.fieldName
}
</script>

<template>
  <UForm ref="retForm" :state="state" :schema="ProjectCreateRetrievalStrategySchema" :validate-on="['input']"
    @error="console.log" @submit="onSubmit">
    <div class="flex gap-4 items-baseline">
      <UFormField name="n_shot_prompts"
        :label="`N Shot Prompts ${state?.n_shot_prompts?.length === 0 || state?.n_shot_prompts === undefined ? '' : `(${state?.n_shot_prompts?.length})`}`"
        class="flex-1 my-0">
        <template #label="{ label }">
          <div class="flex items-center">
            {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
            <FieldTooltip @show-tooltip="handleTooltip" field-name="n_shot_prompts"/>
          </div>
        </template>
        <USelectMenu :search-input="false" v-model="state.n_shot_prompts" value-key="value" multiple
          :items="meta.retrievalStrategy.shotPrompts" class="w-full primary-dropdown my-0" />
        <!-- <template #hint>
          <FieldTooltip field-name="n_shot_prompts" />
        </template> -->
      </UFormField>
      <UFormField name="n_shot_prompt_guide" label="Shot Prompt File" class="flex-1">
        <PromptGuideSelect v-model="state.n_shot_prompt_guide" :required-prompts="selectedMaxShotPrompts"
          @error="handlePromptGuideError" />
        <!-- <template #hint>
          <PromptGuideHelp />
        </template> -->
        <template #label="{ label }">
          <div class="flex items-center">
            {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
            <FieldTooltip @show-tooltip="handleTooltip" field-name="n_shot_prompt_guide"/>
          </div>
        </template>
      </UFormField>
    </div>
    <template v-if="props.kbModel !=='none'">
    <UFormField name="knn_num"
      :label="`KNN ${state?.knn_num?.length === 0 || state?.knn_num === undefined ? '' : `(${state?.knn_num?.length})`}`"
      >
      <USelectMenu :search-input="false" v-model="state.knn_num" value-key="value" multiple :items="meta.retrievalStrategy.knnNumber"
        class="w-full primary-dropdown" />
      <template #label="{ label }">
        <div class="flex items-center">
          {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
          <FieldTooltip @show-tooltip="handleTooltip" field-name="knn_num"/>
        </div>
      </template>
    </UFormField>
    <UFormField name="rerank_model_id" :label="`Reranking Model ${region === 'us-east-1' ? `(Reranking is not available in us-east-1)`:``}`" :required="region !== 'us-east-1'">
      <USelectMenu :search-input="false" :disabled="region === 'us-east-1'" v-model="state.rerank_model_id" value-key="value" multiple
        :items="useFilteredRerankModels(region)" class="w-full primary-dropdown" />
      <template #label="{ label }">
        <div class="flex items-center">
          {{ label }} <span v-if="region !== 'us-east-1'" class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
          <FieldTooltip @show-tooltip="handleTooltip" field-name="rerank_model_id"/>
        </div>
      </template>
    </UFormField>
    </template>
    <UFormField name="retrieval"
      :label="`Inferencing Model ${state?.retrieval?.length === 0 || state?.retrieval === undefined ? '' : `(${state?.retrieval?.length})`}`"
      >
      <ModelSelect v-model="state.retrieval" model="retrieval" />
      <template #label="{ label }">
        <div class="flex items-center">
          {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
          <FieldTooltip @show-tooltip="handleTooltip" field-name="retrieval"/>
        </div>
      </template>
      <!-- <template #hint>
        <FieldTooltip field-name="retrieval" />
      </template> -->
    </UFormField>
    <UFormField name="temp_retrieval_llm"
      :label="`Inferencing Model Temperature ${state?.temp_retrieval_llm?.length === 0 || state?.temp_retrieval_llm === undefined ? '' : `(${state?.temp_retrieval_llm?.length})`}`"
      >
      <USelectMenu :search-input="false" v-model="state.temp_retrieval_llm" value-key="value" multiple
        :items="meta.retrievalStrategy.temperature" class="w-full primary-dropdown" />
      <template #label="{ label }">
        <div class="flex items-center">
          {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
          <FieldTooltip @show-tooltip="handleTooltip" field-name="temp_retrieval_llm"/>
        </div>
      </template>
      <!-- <template #hint>
        <FieldTooltip field-name="temp_retrieval_llm" />
      </template> -->
    </UFormField>
    <!-- <UFormField name="region-selected" label="Selected Region">
      <UInput v-model="state.region"/>
    </UFormField> -->
    <div class="flex justify-between items-center w-full mt-6">
      <div>
        <UButton v-if="showBackButton" type="button" icon="i-lucide-arrow-left" label="Back" class="secondary-btn"
          @click.prevent="emits('previous')" />
      </div>
      <div>
        <UButton trailing-icon="i-lucide-arrow-right" :label="nextButtonLabel" type="submit" class="primary-btn" />
      </div>
    </div>
  </UForm>
</template>
