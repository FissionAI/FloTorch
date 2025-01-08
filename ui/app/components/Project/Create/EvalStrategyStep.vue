<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui';
import {  useMutation } from '@tanstack/vue-query';

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
  guardrails : modelValue.value?.guardrails || []
})

const emits = defineEmits(["next", "previous"])

const onSubmit = (event: FormSubmitEvent<ProjectCreateEval>) => {
  modelValue.value = event.data
  emits("next")
}

const guardrailsList = ref([]);

const { mutateAsync: getGuardrailsList, isPending: isFetchingGuardrailsList } = useMutation({
  mutationFn: async () => {
    const response = await useGuardrailsList()    
    guardrailsList.value = response?.map(item=>{
      return {
        label : item.name,
        value : item.name,
        name : item.name,
        guardrails_id: item.guardrails_id,
        guardrail_version: item.version,
        enable_prompt_guardrails: true,
        enable_context_guardrails: true,
        enable_response_guardrails: true
      }
    })
    return response
  }
})

const fetchGuardrails = ()=>{
  state.guardrails = [];
   getGuardrailsList()
}

onMounted(() => {
  fetchGuardrails()
})

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
      <div class="flex gap-2 items-center w-full">
      <UFormField name="guardrails"
        :label="`Guardrails ${state?.guardrails?.length === 0 || state?.guardrails === undefined ? '' : `(${state?.guardrails?.length})`}`"
         class="text-ellipsis overflow-hidden flex-11">
        <USelectMenu v-model="state.guardrails" :disabled="isFetchingGuardrailsList" :loading="isFetchingGuardrailsList"  multiple
          :items="guardrailsList" class="w-full"
          placeholder="None"
           />
        <template #hint>
          <FieldTooltip field-name="guardrails" />
        </template>
      </UFormField>
      <UFormField name="refetch_guardrail_list" label=" " class="flex-1" >
        <UButton 
        class="w-full mt-8"
          label="Refresh" 
          trailing-icon="i-lucide-repeat-2" 
          @click.prevent="fetchGuardrails"
          />
      </UFormField>
      </div>
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
