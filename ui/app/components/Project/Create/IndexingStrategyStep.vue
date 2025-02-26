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
  hierarchical_parent_chunk_size: modelValue.value.hierarchical_parent_chunk_size || undefined,
  hierarchical_child_chunk_size: modelValue.value.hierarchical_child_chunk_size || undefined,
  hierarchical_chunk_overlap_percentage: modelValue.value.hierarchical_chunk_overlap_percentage || undefined,
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

const tooltip = ref('')
const fieldName = ref('')

const handleTooltip = (tooltipInfo: {tooltip: string, fieldName: string}) => {
  tooltip.value = tooltipInfo.tooltip
  fieldName.value = tooltipInfo.fieldName
}

const meta = useProjectCreateMeta()

</script>

<template>
  <UForm :state="state" :schema="ProjectCreateIndexingStrategySchema" :validate-on="['input']" @submit="onSubmit"
    @error="console.log">
    <UFormField name="chunking_strategy"
      :label="`Chunking ${state?.chunking_strategy?.length === 0 || state?.chunking_strategy === undefined ? '' : `(${state?.chunking_strategy?.length})`}`"
      >
      <USelectMenu :search-input="false" v-model="state.chunking_strategy" value-key="value" multiple
        :items="meta.indexingStrategy.chunkingStrategy" class="w-full primary-dropdown mt-1" />
      <template #label="{ label }">
        <div class="flex items-center">
          {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
          <FieldTooltip @show-tooltip="handleTooltip" field-name="chunking_strategy"/>
        </div>
      </template>
      <!-- <template #hint>
        <FieldTooltip field-name="chunking_strategy" />
      </template> -->
    </UFormField>
    <div v-if="state.chunking_strategy?.includes('fixed')">
      <UCard>
      <label class="font-bold text-sm"> Fixed Chunking Settings </label>
        <UFormField name="chunk_size"
      :label="`Chunk Size (Tokens) ${state?.chunk_size?.length === 0 || state?.chunk_size === undefined ? '' : `(${state?.chunk_size?.length})`}`"
      >
      <USelectMenu :search-input="false" v-model="state.chunk_size" value-key="value" multiple :items="meta.indexingStrategy.chunkSize"
        class="w-full primary-dropdown mt-1 mb-3" />
      <template #label="{ label }">
        <div class="flex items-center">
          {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
          <FieldTooltip @show-tooltip="handleTooltip" field-name="fixed_chunk_size"/>
        </div>
      </template>
      <!-- <template #hint>
        <FieldTooltip field-name="chunk_size" />
      </template> -->
    </UFormField>
    <UFormField name="chunk_overlap"
      :label="`Chunk Overlap Percentage ${state?.chunk_overlap?.length === 0 || state?.chunk_overlap === undefined ? '' : `(${state?.chunk_overlap?.length})`}`"
      >
      <USelectMenu :search-input="false" v-model="state.chunk_overlap" value-key="value" multiple
        :items="meta.indexingStrategy.chunkOverlapPercentage" class="w-full primary-dropdown mt-1" >
        </USelectMenu>
      <template #label="{ label }">
        <div class="flex items-center">
          {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
          <FieldTooltip @show-tooltip="handleTooltip" field-name="fixed_chunk_overlap_percentage"/>
        </div>
      </template>
      <!-- <template #hint>
            <FieldTooltip field-name="chunk_overlap" />
          </template> -->
        </UFormField>
      </UCard>
    </div>
    
    <div v-if="state.chunking_strategy?.includes('hierarchical')">
      <UCard>
       <label class="font-bold text-sm"> Hierarchical Chunking Settings  </label>
      <UFormField name="hierarchical_child_chunk_size"
        :label="`Child Chunk Size (Tokens) ${state?.hierarchical_child_chunk_size?.length === 0 || state?.hierarchical_child_chunk_size === undefined ? '' : `(${state?.hierarchical_child_chunk_size?.length})`}`"
        >
        <USelectMenu :search-input="false" v-model="state.hierarchical_child_chunk_size" value-key="value" multiple
        :items="meta.indexingStrategy.hierarchical_child_chunk_size" class="w-full primary-dropdown mt-1 mb-3" />
        <template #label="{ label }">
          <div class="flex items-center">
            {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
            <FieldTooltip @show-tooltip="handleTooltip" field-name="hierarchical_child_chunk_size"/>
          </div>
        </template>
      </UFormField>
       <UFormField name="hierarchical_parent_chunk_size"
      :label="`Parent Chunk Size (Tokens) ${state?.hierarchical_parent_chunk_size?.length === 0 || state?.hierarchical_parent_chunk_size === undefined ? '' : `(${state?.hierarchical_parent_chunk_size?.length})`}`"
      >
        <USelectMenu :search-input="false" v-model="state.hierarchical_parent_chunk_size" value-key="value" multiple
          :items="meta.indexingStrategy.hierarchical_parent_chunk_size" class="w-full primary-dropdown mt-1 mb-3" />
        <template #label="{ label }">
          <div class="flex items-center">
            {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
            <FieldTooltip @show-tooltip="handleTooltip" field-name="hierarchical_parent_chunk_size"/>
          </div>
        </template>
      </UFormField>
      <UFormField name="hierarchical_chunk_overlap_percentage"
        :label="` Chunk Overlap Percentage ${state?.hierarchical_chunk_overlap_percentage?.length === 0 || state?.hierarchical_chunk_overlap_percentage === undefined ? '' : `(${state?.hierarchical_chunk_overlap_percentage?.length})`}`"
        >
        <USelectMenu :search-input="false" v-model="state.hierarchical_chunk_overlap_percentage" value-key="value" multiple
        :items="meta.indexingStrategy.hierarchical_chunk_overlap_percentage" class="w-full primary-dropdown mt-1">
        </USelectMenu>
        <template #label="{ label }">
          <div class="flex items-center">
            {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
            <FieldTooltip @show-tooltip="handleTooltip" field-name="hierarchical_chunk_overlap_percentage"/>
          </div>
        </template>
      </UFormField>
      </UCard>
    </div>
    <UFormField name="embedding"
      :label="`Embedding Model ${state?.embedding?.length === 0 || state?.embedding === undefined ? '' : `(${state?.embedding?.length})`}`"
      >
      <ModelSelect v-model="state.embedding" model="embedding" />
      <template #label="{ label }">
        <div class="flex items-center">
          {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
          <FieldTooltip @show-tooltip="handleTooltip" field-name="embedding"/>
        </div>
      </template>
      <!-- <template #hint>
        <FieldTooltip field-name="embedding" />
      </template> -->
    </UFormField>
    <UFormField name="vector_dimension"
      :label="`Vector Dimension ${state?.vector_dimension?.length === 0 || state?.vector_dimension === undefined ? '' : `(${state?.vector_dimension?.length})`}`"
      >
      <VectorDimensionSelect v-model="state.vector_dimension" />
      <template #label="{ label }">
        <div class="flex items-center">
          {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
          <FieldTooltip @show-tooltip="handleTooltip" field-name="vector_dimension"/>
        </div>
      </template>
      <!-- <template #hint>
        <FieldTooltip field-name="vector_dimension" />
      </template> -->
    </UFormField>
    <UFormField name="indexing_algorithm"
      :label="`Indexing Algorithm ${state?.indexing_algorithm?.length === 0 || state?.indexing_algorithm === undefined ? '' : `(${state?.indexing_algorithm?.length})`}`"
      >
      <USelectMenu :search-input="false" v-model="state.indexing_algorithm" value-key="value" multiple
        :items="meta.indexingStrategy.indexingAlgorithms" class="w-full primary-dropdown mt-1" />
      <template #label="{ label }">
        <div class="flex items-center">
          {{ label }} <span class="italic"> - required</span>
          <span class="w-[1px] h-3 ml-2 bg-gray-400"></span>
          <FieldTooltip @show-tooltip="handleTooltip" field-name="indexing_algorithm"/>
        </div>
      </template>
      <!-- <template #hint>
        <FieldTooltip field-name="indexing_algorithm" />
      </template> -->
    </UFormField>
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
