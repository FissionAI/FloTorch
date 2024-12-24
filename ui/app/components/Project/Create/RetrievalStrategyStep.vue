<script setup lang="ts">
import type { FormError, FormSubmitEvent } from '@nuxt/ui';
import { useMax } from '@vueuse/math'


withDefaults(defineProps<{
  showBackButton?: boolean,
  nextButtonLabel?: string,
  region?: string,
}>(), {
  showBackButton: true,
  nextButtonLabel: "Next",
  region:'us-east-1',
})

const emits = defineEmits(['previous', 'next'])
const errorMsg = ref("");

const modelValue = defineModel<ProjectCreateRetrievalStrategy>({
  default: () => {
    return {}
  }
})

const state = reactive<ProjectCreateRetrievalStrategy>({
  knn_num: modelValue.value.knn_num || undefined,
  retrieval: modelValue.value.retrieval || undefined,
  n_shot_prompts: modelValue.value.n_shot_prompts || undefined,
  n_shot_prompt_guide: modelValue.value.n_shot_prompt_guide || undefined,
  temp_retrieval_llm: modelValue.value.temp_retrieval_llm || undefined,
  rerank_model_id: modelValue.value.rerank_model_id || undefined,
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
</script>



<template>
  <UForm ref="retForm" :state="state" :schema="ProjectCreateRetrievalStrategySchema" :validate-on="['input']"
    @error="console.log" @submit="onSubmit">
    <div class="flex gap-4 items-baseline">
      <UFormField name="n_shot_prompts"
        :label="`N Shot Prompts ${state?.n_shot_prompts?.length === 0 || state?.n_shot_prompts === undefined ? '' : `(${state?.n_shot_prompts?.length})`}`"
        required class="flex-1">
        <USelectMenu v-model="state.n_shot_prompts" value-key="value" multiple
          :items="meta.retrievalStrategy.shotPrompts" class="w-full" />
        <template #hint>
          <FieldTooltip field-name="n_shot_prompts" />
        </template>
      </UFormField>
      <UFormField name="n_shot_prompt_guide" label="Shot Prompt File" required class="flex-1">
        <PromptGuideSelect v-model="state.n_shot_prompt_guide" :required-prompts="selectedMaxShotPrompts"
          @error="handlePromptGuideError" />
        <template #hint>
          <PromptGuideHelp />
        </template>
      </UFormField>
    </div>
    <UFormField name="knn_num"
      :label="`KNN ${state?.knn_num?.length === 0 || state?.knn_num === undefined ? '' : `(${state?.knn_num?.length})`}`"
      required>
      <USelectMenu v-model="state.knn_num" value-key="value" multiple :items="meta.retrievalStrategy.knnNumber"
        class="w-full" />
      <template #hint>
        <FieldTooltip field-name="knn_num" />
      </template>
    </UFormField>
    <UFormField name="retrieval"
      :label="`Inferencing LLM ${state?.retrieval?.length === 0 || state?.retrieval === undefined ? '' : `(${state?.retrieval?.length})`}`"
      required>
      <ModelSelect v-model="state.retrieval" model="retrieval" />
      <template #hint>
        <FieldTooltip field-name="retrieval" />
      </template>
    </UFormField>
    <UFormField name="temp_retrieval_llm"
      :label="`Inferencing LLM Temperature ${state?.temp_retrieval_llm?.length === 0 || state?.temp_retrieval_llm === undefined ? '' : `(${state?.temp_retrieval_llm?.length})`}`"
      required>
      <USelectMenu v-model="state.temp_retrieval_llm" value-key="value" multiple
        :items="meta.retrievalStrategy.temperature" class="w-full" />
      <template #hint>
        <FieldTooltip field-name="temp_retrieval_llm" />
      </template>
    </UFormField>
    <UFormField name="rerank_model_id" label="Rerank Model" required>
      <USelectMenu v-model="state.rerank_model_id" value-key="value" multiple
        :items="useFilteredRerankModels(region)" class="w-full" />
      <template #hint>
        <FieldTooltip field-name="rerank_model_id" />
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
