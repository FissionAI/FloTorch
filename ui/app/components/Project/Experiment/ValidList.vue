<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui';
const UCheckbox = resolveComponent('UCheckbox')
const UButton = resolveComponent('UButton')

const toast = useToast()
const modelValue = defineModel<ValidExperiment[]>()

const props = defineProps<{
  selectable?: boolean
  experiments?: ValidExperiment[]
  loading?: boolean
}>()

const isLoading = computed(() => props.loading ?? false)
const table = useTemplateRef('table')

watchEffect(() => {
  if (table?.value?.tableApi && table.value.tableApi.getFilteredSelectedRowModel().rows) {
    modelValue.value = table.value.tableApi.getFilteredSelectedRowModel().rows.map((row: any) => {
      return row.original
    })
  }
})

const columns = ref<TableColumn<ValidExperiment>[]>([
  {
    id: 'select',
    header: ({ table }) => {
      if(props.experiments?.length! < 39) {
        return h(UCheckbox, {
          'modelValue': table.getIsAllPageRowsSelected(),
          'indeterminate': table.getIsSomePageRowsSelected(),
          'onUpdate:modelValue': (value: boolean) => table.toggleAllPageRowsSelected(!!value),
          'ariaLabel': 'Select all'
        })
      }else {
        return 
      }
        
    },
    cell: ({ row }) => h(UCheckbox, {
      'modelValue': row.getIsSelected(),
      'onUpdate:modelValue': (value: boolean) => {
        const selectedRows = table.value?.tableApi?.getFilteredSelectedRowModel().rows ?? [];
        if (value && selectedRows.length > 39) {
          toast.add({
            title: 'Max limit reached',
            description: `You can select upto 40 experiments`,
            color: 'error'
          })
          return;
        }
        row.toggleSelected(!!value);
      },
      'ariaLabel': 'Select row'
    }),
    enableHiding: false,
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Chunking",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "chunking_strategy",
    label: "Chunking"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Chunk Size",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "chunk_size",
    label: "Chunk Size"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Chunk\nOverlap Percentage",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        style: "white-space: pre !important",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "chunk_overlap",
    label: "Chunk Overlap Percentage"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Embedding Model",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "embedding_model",
    label: "Embedding Model"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Vector Dimensions",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "vector_dimension",
    label: "Vector Dimensions"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Indexing Algorithm",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "indexing_algorithm",
    label: "Indexing Algorithm"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "N Shot Prompts",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "n_shot_prompts",
    label: "N Shot Prompts"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "KNN",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "knn_num",
    label: "KNN"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Inferencing Model",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "retrieval_model",
    label: "Inferencing Model"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Inferencing Model Temperature",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "temp_retrieval_llm",
    label: "Inferencing Model Temperature"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Evaluation Service",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "eval_service",
    label: "Evaluation Service"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Evaluation Embedding Model",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "eval_embedding_model",
    label: "Evaluation Embedding Model"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Evaluation Retrieval Model",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "eval_retrieval_model",
    label: "Evaluation Retrieval Model"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Directional Pricing",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "directional_pricing",
    label: "Directional Pricing"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Region",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "region",
    label: "Region"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Reranking Model",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    enableHiding: true,
    accessorKey: "rerank_model_id",
    label: "Reranking Model"
  }
])

const columnVisibility = ref({
  select: props.selectable ?? false,
  directional_pricing: false,
  region: false,
  rerank_model_id: false,
  eval_retrieval_model: false,
  eval_embedding_model: false,
  eval_service:false,
  n_shot_prompts: false,
  knn_num: false,
  indexing_algorithm: false,
  temp_retrieval_llm: false,
})
</script>

<template>
  <div class="space-y-3">
    <div class="flex justify-between">
      <p><span class="font-medium">Region:</span> {{ experiments?.[0]?.region}}</p>
      <UDropdownMenu :items="table?.tableApi
        ?.getAllColumns()
        .filter((column: any) => column.getCanHide())
        .map((column: any) => ({
          label: column.columnDef.label,
          type: 'checkbox' as const,
          checked: column.getIsVisible(),
          onUpdateChecked(checked: boolean) {
            table?.tableApi?.getColumn(column.id)?.toggleVisibility(!!checked)
          },
          onSelect(e?: Event) {
            e?.preventDefault()
          }
        }))
        " :content="{ align: 'end' }">
        <UButton label="Columns" color="neutral" variant="outline" trailing-icon="i-lucide-chevron-down" />
      </UDropdownMenu>
    </div>
    <UTable class="h-100" sticky ref="table" v-model:column-visibility="columnVisibility" :columns="columns" :data="experiments"
      :loading="isLoading">
      <template #directional_pricing-cell="{ row }">
        <!-- {{ useHumanCurrencyAmount(row.original.directional_pricing) }} -->
        <ProjectExperimentDirectionalPricing :label="'Directional Pricing'" :pricing-info="{
          retrieval_cost_estimate : row.original?.retrieval_cost_estimate,
          indexing_cost_estimate : row.original?.indexing_cost_estimate,
          eval_cost_estimate : row.original?.eval_cost_estimate
        }" :price="row.original?.directional_pricing ? row.original.directional_pricing : '-'" />
      </template>
      <template #chunking_strategy-cell="{ row }">
        {{ useHumanChunkingStrategy(row.original.chunking_strategy) }}
      </template>
      <template #chunk_size-cell="{ row }">
        {{ useHumanChunkingStrategy(row.original.chunking_strategy) === 'Fixed' ? row.original.chunk_size : [row.original.hierarchical_child_chunk_size, row.original.hierarchical_parent_chunk_size] }}
      </template>
       <template #chunk_overlap-cell="{ row }">
          {{ useHumanChunkingStrategy(row.original.chunking_strategy) === 'Fixed' ? row.original.chunk_overlap : row.original.hierarchical_chunk_overlap_percentage}}
      </template>
      <template #indexing_algorithm-cell="{ row }">
        {{ useHumanIndexingAlgorithm(row.original.indexing_algorithm) }}
      </template>
      <template #embedding_model-cell="{ row }">
        {{ useModelName("indexing", row.original.embedding_model) }}
      </template>
      <template #retrieval_model-cell="{ row }">
        {{ useModelName("retrieval", row.original.retrieval_model) }}
      </template>
       <!-- <template #eval_cost_estimate-cell="{ row }">
        {{ useHumanCurrencyAmount(row.original.eval_cost_estimate) }}
      </template>
       <template #indexing_cost_estimate-cell="{ row }">
        {{ useHumanCurrencyAmount(row.original.indexing_cost_estimate) }}
      </template>
       <template #retrieval_cost_estimate-cell="{ row }">
        {{ useHumanCurrencyAmount(row.original.retrieval_cost_estimate) }}
      </template> -->
    </UTable>
  </div>
</template>

<style scoped>
span.truncate {
  white-space: pre-wrap !important;
  word-break: break-word !important;
}
</style>
