<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui';
import { useQuery, useMutation } from '@tanstack/vue-query';

const meta = useProjectCreateMeta()
const modelValue = defineModel<ProjectCreateEval>({
  default: () => {
    return {}
  }
})

const props = withDefaults(defineProps<{
  showBackButton?: boolean,
  nextButtonLabel?: string,
  inferenceModel?: string[],
  embeddingModel?: string[],
}>(), {
  showBackButton: true,
  nextButtonLabel: "Next",
  inferenceModel: [],
  embeddingModel: [],
})

const state = reactive<Partial<ProjectCreateEval>>({
  service: modelValue.value?.service || undefined,
  ragas_embedding_llm: modelValue.value?.ragas_embedding_llm || undefined,
  ragas_inference_llm: modelValue.value?.ragas_inference_llm || undefined,
})

const emits = defineEmits(["next", "previous"])

const onSubmit = (event: FormSubmitEvent<ProjectCreateEval>) => {
  modelValue.value = event.data
  emits("next")
}
</script>



<template>
  <UForm :schema="ProjectCreateEvalSchema" :state="state" :validate-on="['input']" @submit="onSubmit">
    <UFormField name="service"
        :label="`Service`"
        required>
        <USelectMenu v-model="state.service" value-key="value"
        :items="meta.evalStrategy.service" class="w-full" />
        <template #hint>
          <FieldTooltip field-name="service" />
        </template>
      </UFormField>
    <UFormField name="ragas_embedding_llm"
        :label="`Ragas Embedding LLM`"
        required>
        <USelectMenu v-model="state.ragas_embedding_llm" value-key="value"
        :items="useFilteredRagasEmbeddingModels(embeddingModel)" class="w-full" />
        <template #hint>
          <FieldTooltip field-name="ragas_embedding_llm" />
        </template>
      </UFormField>
    <UFormField name="ragas_inference_llm"
        :label="`Ragas Inference LLM`"
        required>
        <USelectMenu v-model="state.ragas_inference_llm" value-key="value"
        :items="useFilteredRagasInferenceModels(inferenceModel)" class="w-full" />
        <template #hint>
          <FieldTooltip field-name="ragas_inference_llm" />
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
