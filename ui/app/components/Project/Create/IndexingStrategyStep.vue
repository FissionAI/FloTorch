<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui';

withDefaults(defineProps<{
  showBackButton?: boolean,
  nextButtonLabel?: string
}>(), {
  showBackButton: true,
  nextButtonLabel: "Next"
})

const modelValue = defineModel<ProjectCreateIndexingStrategy>({
  default: () => {
    return {}
  }
})

const state = reactive<Partial<ProjectCreateIndexingStrategy>>({
  chunk_overlap: modelValue.value.chunk_overlap || undefined,
  chunk_size: modelValue.value.chunk_size || undefined,
  embedding: modelValue.value.embedding || undefined,
  chunking_strategy: modelValue.value.chunking_strategy || undefined,
  vector_dimension: modelValue.value.vector_dimension || undefined,
  indexing_algorithm: modelValue.value.indexing_algorithm || undefined,
})

const emits = defineEmits(['previous', 'next'])


const onSubmit = (event: FormSubmitEvent<ProjectCreateIndexingStrategy>) => {
  modelValue.value = event.data
  emits('next', event.data)
}

const meta = useProjectCreateMeta()

</script>

<template>
  <UForm :state="state" :schema="ProjectCreateIndexingStrategySchema" :validate-on="['input']" @submit="onSubmit"
    @error="console.log">
    <UFormField name="chunking_strategy"
      :label="`Chunking ${state?.chunking_strategy?.length === 0 || state?.chunking_strategy === undefined ? '' : `(${state?.chunking_strategy?.length})`}`"
      required>
      <USelectMenu v-model="state.chunking_strategy" value-key="value" multiple
        :items="meta.indexingStrategy.chunkingStrategy" class="w-full" />
      <template #hint>
        <FieldTooltip field-name="chunking_strategy" />
      </template>
    </UFormField>
    <UFormField name="chunk_size"
      :label="`Chunk Size ${state?.chunk_size?.length === 0 || state?.chunk_size === undefined ? '' : `(${state?.chunk_size?.length})`}`"
      required>
      <USelectMenu v-model="state.chunk_size" value-key="value" multiple :items="meta.indexingStrategy.chunkSize"
        class="w-full" />
      <template #hint>
        <FieldTooltip field-name="chunk_size" />
      </template>
    </UFormField>
    <UFormField name="chunk_overlap"
      :label="`Chunk Overlap Percentage ${state?.chunk_overlap?.length === 0 || state?.chunk_overlap === undefined ? '' : `(${state?.chunk_overlap?.length})`}`"
      required>
      <USelectMenu v-model="state.chunk_overlap" value-key="value" multiple
        :items="meta.indexingStrategy.chunkOverlapPercentage" class="w-full" />
      <template #hint>
        <FieldTooltip field-name="chunk_overlap" />
      </template>
    </UFormField>
    <UFormField name="embedding"
      :label="`Embedding Model ${state?.embedding?.length === 0 || state?.embedding === undefined ? '' : `(${state?.embedding?.length})`}`"
      required>
      <ModelSelect v-model="state.embedding" model="embedding" />
      <template #hint>
        <FieldTooltip field-name="embedding" />
      </template>
    </UFormField>
    <UFormField name="vector_dimension"
      :label="`Vector Dimensions ${state?.vector_dimension?.length === 0 || state?.vector_dimension === undefined ? '' : `(${state?.vector_dimension?.length})`}`"
      required>
      <VectorDimensionSelect v-model="state.vector_dimension" />
      <template #hint>
        <FieldTooltip field-name="vector_dimension" />
      </template>
    </UFormField>
    <UFormField name="indexing_algorithm"
      :label="`Indexing Algorithm ${state?.indexing_algorithm?.length === 0 || state?.indexing_algorithm === undefined ? '' : `(${state?.indexing_algorithm?.length})`}`"
      required>
      <USelectMenu v-model="state.indexing_algorithm" value-key="value" multiple
        :items="meta.indexingStrategy.indexingAlgorithms" class="w-full" />
      <template #hint>
        <FieldTooltip field-name="indexing_algorithm" />
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
