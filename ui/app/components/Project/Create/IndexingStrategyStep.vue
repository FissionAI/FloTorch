<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui";

withDefaults(
  defineProps<{
    showBackButton?: boolean;
    nextButtonLabel?: string;
  }>(),
  {
    showBackButton: true,
    nextButtonLabel: "Next",
  }
);

const modelValue = defineModel<ProjectCreateIndexingStrategy>({
  default: () => {
    return {};
  },
});

const state = reactive<Partial<ProjectCreateIndexingStrategy>>({
  chunk_overlap: modelValue.value.chunk_overlap || undefined,
  chunk_size: modelValue.value.chunk_size || undefined,
  hierarchical_parent_chunk_size:
    modelValue.value.hierarchical_parent_chunk_size || undefined,
  hierarchical_child_chunk_size:
    modelValue.value.hierarchical_child_chunk_size || undefined,
  hierarchical_chunk_overlap_percentage:
    modelValue.value.hierarchical_chunk_overlap_percentage || undefined,
  embedding: modelValue.value.embedding || undefined,
  chunking_strategy: modelValue.value.chunking_strategy || undefined,
  vector_dimension: modelValue.value.vector_dimension || undefined,
  indexing_algorithm: modelValue.value.indexing_algorithm || undefined,
});

const emits = defineEmits(["previous", "next"]);

const onSubmit = (event: FormSubmitEvent<ProjectCreateIndexingStrategy>) => {
  modelValue.value = event.data;
  emits("next", event.data);
};

const meta = useProjectCreateMeta();

const validate_fixed_chunking_strategy = computed(() => {
  if (!state.chunking_strategy || !state?.chunking_strategy.length) {
    return false;
  } else if (state.chunking_strategy.includes('fixed')) {
    if (!state.chunk_overlap || !state?.chunk_overlap.length) {
      return false;
    }
  } else if (state.chunking_strategy.includes('hierarchical')) {
    if (
      (!state.hierarchical_parent_chunk_size || !state?.hierarchical_parent_chunk_size.length) ||
      (!state.hierarchical_child_chunk_size || !state?.hierarchical_child_chunk_size.length) || 
      (!state.hierarchical_chunk_overlap_percentage || !state?.hierarchical_chunk_overlap_percentage.length)
    ) {
      return false;
    }
  }
  // If no conditions return false, return true or any other appropriate value
  return true;
});




const validForm = computed(() => {
  if (
    !state?.embedding ||
    !validate_fixed_chunking_strategy.value ||
    !state?.vector_dimension ||
    !state?.indexing_algorithm
  ) {
    return false;
  } else if (
   !validate_fixed_chunking_strategy.value || 
    !state?.embedding.length ||
    !state?.chunking_strategy.length ||
    !state?.vector_dimension.length ||
    !state?.indexing_algorithm.length
  ) {
    return false;
  }
  return true;
});
</script>

<template>
  <UForm
    :state="state"
    :schema="ProjectCreateIndexingStrategySchema"
    :validate-on="['input']"
    @submit="onSubmit"
    @error="console.log"
  >
    <UFormField
      name="chunking_strategy"
      :label="`Chunking ${state?.chunking_strategy?.length === 0 || state?.chunking_strategy === undefined ? '' : `(${state?.chunking_strategy?.length})`}`"
      required
    >
      <USelectMenu
        v-model="state.chunking_strategy"
        value-key="value"
        multiple
        :items="meta.indexingStrategy.chunkingStrategy"
        class="w-full"
      />
      <template #hint>
        <FieldTooltip field-name="chunking_strategy" />
      </template>
    </UFormField>
    <div v-if="state.chunking_strategy?.includes('fixed')">
      <UCard>
        <UFormField
          name="chunk_size"
          :label="`Chunk Size ${state?.chunk_size?.length === 0 || state?.chunk_size === undefined ? '' : `(${state?.chunk_size?.length})`}`"
          required
        >
          <USelectMenu
            v-model="state.chunk_size"
            value-key="value"
            multiple
            :items="meta.indexingStrategy.chunkSize"
            class="w-full"
          />
          <template #hint>
            <FieldTooltip field-name="chunk_size" />
          </template>
        </UFormField>
        <UFormField
          name="chunk_overlap"
          :label="`Chunk Overlap Percentage ${state?.chunk_overlap?.length === 0 || state?.chunk_overlap === undefined ? '' : `(${state?.chunk_overlap?.length})`}`"
          required
        >
          <USelectMenu
            v-model="state.chunk_overlap"
            value-key="value"
            multiple
            :items="meta.indexingStrategy.chunkOverlapPercentage"
            class="w-full"
          />
          <template #hint>
            <FieldTooltip field-name="chunk_overlap" />
          </template>
        </UFormField>
      </UCard>
    </div>

    <div v-if="state.chunking_strategy?.includes('hierarchical')">
      <UCard>
        <UFormField
          name="hierarchical_parent_chunk_size"
          :label="`Hierarchical Parent Chunk Size ${state?.hierarchical_parent_chunk_size?.length === 0 || state?.hierarchical_parent_chunk_size === undefined ? '' : `(${state?.hierarchical_parent_chunk_size?.length})`}`"
          required
        >
          <USelectMenu
            v-model="state.hierarchical_parent_chunk_size"
            value-key="value"
            multiple
            :items="meta.indexingStrategy.hierarchical_parent_chunk_size"
            class="w-full"
          />
          <template #hint>
            <FieldTooltip field-name="hierarchical_parent_chunk_size" />
          </template>
        </UFormField>
        <UFormField
          name="hierarchical_child_chunk_size"
          :label="`Hierarchical Child Chunk Size ${state?.hierarchical_child_chunk_size?.length === 0 || state?.hierarchical_child_chunk_size === undefined ? '' : `(${state?.hierarchical_child_chunk_size?.length})`}`"
          required
        >
          <USelectMenu
            v-model="state.hierarchical_child_chunk_size"
            value-key="value"
            multiple
            :items="meta.indexingStrategy.hierarchical_child_chunk_size"
            class="w-full"
          />
          <template #hint>
            <FieldTooltip field-name="hierarchical_child_chunk_size" />
          </template>
        </UFormField>
        <UFormField
          name="hierarchical_chunk_overlap_percentage"
          :label="`Hierarchical Chunk Overlap Percentage ${state?.hierarchical_chunk_overlap_percentage?.length === 0 || state?.hierarchical_chunk_overlap_percentage === undefined ? '' : `(${state?.hierarchical_chunk_overlap_percentage?.length})`}`"
          required
        >
          <USelectMenu
            v-model="state.hierarchical_chunk_overlap_percentage"
            value-key="value"
            multiple
            :items="meta.indexingStrategy.hierarchical_chunk_overlap_percentage"
            class="w-full"
          />
          <template #hint>
            <FieldTooltip field-name="hierarchical_chunk_overlap_percentage" />
          </template>
        </UFormField>
      </UCard>
    </div>
    <UFormField
      name="embedding"
      :label="`Embedding Model ${state?.embedding?.length === 0 || state?.embedding === undefined ? '' : `(${state?.embedding?.length})`}`"
      required
    >
      <ModelSelect v-model="state.embedding" model="embedding" />
      <template #hint>
        <FieldTooltip field-name="embedding" />
      </template>
    </UFormField>
    <UFormField
      name="vector_dimension"
      :label="`Vector Dimensions ${state?.vector_dimension?.length === 0 || state?.vector_dimension === undefined ? '' : `(${state?.vector_dimension?.length})`}`"
      required
    >
      <VectorDimensionSelect v-model="state.vector_dimension" />
      <template #hint>
        <FieldTooltip field-name="vector_dimension" />
      </template>
    </UFormField>
    <UFormField
      name="indexing_algorithm"
      :label="`Indexing Algorithm ${state?.indexing_algorithm?.length === 0 || state?.indexing_algorithm === undefined ? '' : `(${state?.indexing_algorithm?.length})`}`"
      required
    >
      <USelectMenu
        v-model="state.indexing_algorithm"
        value-key="value"
        multiple
        :items="meta.indexingStrategy.indexingAlgorithms"
        class="w-full"
      />
      <template #hint>
        <FieldTooltip field-name="indexing_algorithm" />
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
          :disabled="!validForm"
        />
      </div>
    </div>
  </UForm>
</template>
