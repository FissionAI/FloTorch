<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui";
import { useMutation } from "@tanstack/vue-query";

const meta = useProjectCreateMeta();
const modelValue = defineModel<ProjectCreateEval>({
  default: () => {
    return {};
  },
});

const props = withDefaults(
  defineProps<{
    showBackButton?: boolean;
    nextButtonLabel?: string;
    inferenceModel?: string[];
    embeddingModel?: string[];
    region?: string;
  }>(),
  {
    showBackButton: true,
    nextButtonLabel: "Next",
    inferenceModel: [],
    embeddingModel: [],
  }
);

const state = reactive<Partial<ProjectCreateEval>>({
  service: modelValue.value?.service || 'ragas',
  ragas_embedding_llm: modelValue.value?.ragas_embedding_llm || undefined,
  ragas_inference_llm: modelValue.value?.ragas_inference_llm || undefined,
  guardrails: modelValue.value?.guardrails || [],
});

const emits = defineEmits(["next", "previous"]);

const onSubmit = (event: FormSubmitEvent<ProjectCreateEval>) => {
  event.data['guardrails'] = event.data['guardrails'].filter(guardrail=>guardrail.name!=='None')
  modelValue.value = event.data;
  emits("next");
};

const guardrailsList = ref([]);

const { mutateAsync: getGuardrailsList, isPending: isFetchingGuardrailsList } =
  useMutation({
    mutationFn: async () => {
      const response = await useGuardrailsList(props.region);
      guardrailsList.value = response?.map((item) => {
        return {
          label: item.name + ' - ' + item.version,
          value: item.name,
          name: item.name,
          guardrails_id: item.guardrails_id,
          guardrail_version: item.version,
          guardrail_description : item.description,
          enable_prompt_guardrails: true,
          enable_context_guardrails: true,
          enable_response_guardrails: true,
        };
      });
      guardrailsList.value.unshift({
          label: 'None',
          value: 'none',
          name: 'None',
          guardrails_id: null,
          guardrail_version: null,
          guardrail_description : null,
          enable_prompt_guardrails: true,
          enable_context_guardrails: true,
          enable_response_guardrails: true,
      })
      return response;
    },
  });

const fetchGuardrails = () => {
  state.guardrails = [];
  getGuardrailsList();
};

const tooltip = ref('')
const fieldName = ref('')

const handleTooltip = (tooltipInfo: {tooltip: string, fieldName: string}) => {
  tooltip.value = tooltipInfo.tooltip
  fieldName.value = tooltipInfo.fieldName
}

onMounted(() => {
  fetchGuardrails();
});
</script>

<template>
  <UForm
    :schema="ProjectCreateEvalSchema"
    :state="state"
    :validate-on="['input']"
    @submit="onSubmit"
  >
    <UCard class="w-full">
      <!-- <label class="font-bold text-sm -my-4">Guardrails {{ state?.guardrails?.length ? `(${state?.guardrails?.length})` : ''}} - Applied at User Query,Context and Model Response levels</label> -->
      <div class="flex gap-2">
        <UFormField
          :label="`Guardrails ${state?.guardrails?.length ? `(${state?.guardrails?.length})` : ''}`"
          name="guardrails"
          class="text-ellipsis overflow-hidden flex-11"
          required
        >
          <template #label="{ label }">
            <div class="flex items-center">
              {{ label }}<span class="italic"> - required</span>
              <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
              <FieldTooltip @show-tooltip="handleTooltip" field-name="guardrails"/>
            </div>
          </template>
          <USelectMenu
            v-model="state.guardrails"
            :disabled="isFetchingGuardrailsList"
            :loading="isFetchingGuardrailsList"
            multiple
            :items="guardrailsList"
            class="w-full my-3 primary-dropdown"
            :search-input="false"
          >
          
            <template #item-label="{ item }">
                {{ item.label + `${item.guardrail_description ?  ' - ( ' + item.guardrail_description + ')' : ''}` }}
            </template>
          </USelectMenu>
         <div class="my-0">
          <ULink class="text-blue-500 hover:underline" target="_blank" raw :to="`https://${props.region}.console.aws.amazon.com/bedrock/home?region=${props.region}#/guardrails`" active-class="font-bold" inactive-class="text-[var(--ui-text-muted)]">Create guardrails on AWS</ULink>
        </div>
        </UFormField>
        
        <UFormField name="refetch_guardrail_list" label=" " class="flex-1 content-center">
          <UButton
            class="primary-btn"
            label="Fetch Guardrails"
            trailing-icon="i-lucide-repeat-2"
            @click.prevent="fetchGuardrails"
          />
          <!-- <template #hint>
            <FieldTooltip field-name="guardrails" />
          </template> -->
        </UFormField>
      </div>
    </UCard>
    <UCard>
      <!-- <UFormField>
        <template #label>
          <label class="font-bold text-sm">Evaluation</label>
          <FieldTooltip @show-tooltip="handleTooltip" field-name="evaluation"/>
        </template>
        <div class="my-3"></div>
      </UFormField> -->
      <label class="font-bold text-sm">Evaluation</label>
    <div class="my-3">
    <UFormField name="service" :label="`Service`">
      <USelectMenu
        v-model="state.service"
        value-key="value"
        :items="meta.evalStrategy.service"
        class="w-full primary-dropdown my-3"
        :search-input="false"
      />
      <template #label="{ label }">
        <div class="flex items-center">
          {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
          <FieldTooltip @show-tooltip="handleTooltip" field-name="service"/>
        </div>
      </template>
      <!-- <template #hint>
        <FieldTooltip field-name="service" />
      </template> -->
    </UFormField>
    <UFormField
      name="ragas_embedding_llm"
      :label="`Embedding Model`"
    >
      <USelectMenu
        v-model="state.ragas_embedding_llm"
        value-key="value"
        :items="useFilteredRagasEmbeddingModels(embeddingModel)"
        class="w-full primary-dropdown my-3"
        :search-input="false"
      />
      <template #label="{ label }">
        <div class="flex items-center">
          {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
          <FieldTooltip @show-tooltip="handleTooltip" field-name="ragas_embedding_llm"/>
        </div>
      </template>
      <!-- <template #hint>
        <FieldTooltip field-name="ragas_embedding_llm" />
      </template> -->
    </UFormField>
    <UFormField
      name="ragas_inference_llm"
      :label="`Inferencing Model`"
    >
      <USelectMenu
        v-model="state.ragas_inference_llm"
        value-key="value"
        :items="useFilteredRagasInferenceModels(inferenceModel)"
        class="w-full primary-dropdown my-3"
        :search-input="false"
      />
      <template #label="{ label }">
        <div class="flex items-center">
          {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-3 bg-gray-400"></span>
          <FieldTooltip @show-tooltip="handleTooltip" field-name="ragas_inference_llm"/>
        </div>
      </template>
      <!-- <template #hint>
        <FieldTooltip field-name="ragas_inference_llm" />
      </template> -->
    </UFormField>
  </div>
    </UCard>
    <div class="flex justify-between items-center w-full mt-6">
      <div>
        <UButton
          v-if="showBackButton"
          type="button"
          icon="i-lucide-arrow-left"
          label="Back"
          class="secondary-btn"
          @click.prevent="emits('previous')"
        />
      </div>
      <div>
        <UButton
          trailing-icon="i-lucide-arrow-right"
          :label="nextButtonLabel"
          type="submit"
          class="primary-btn"
        />
      </div>
    </div>
  </UForm>
</template>
