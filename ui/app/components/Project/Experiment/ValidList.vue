<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui';
const UCheckbox = resolveComponent('UCheckbox')


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
    header: "Chunking",
    enableHiding: true,
    accessorKey: "chunking_strategy"
  },
  {
    header: "Vector Dimensions",
    enableHiding: true,
    accessorKey: "vector_dimension"
  },
  {
    header: "Chunk Size",
    enableHiding: true,
    accessorKey: "chunk_size"
  },
  {
    header: "Chunk Overlap Percentage",
    enableHiding: true,
    accessorKey: "chunk_overlap"
  },
  {
    header: "Indexing Algorithm",
    enableHiding: true,
    accessorKey: "indexing_algorithm"
  },
  {
    header: "KNN",
    enableHiding: true,
    accessorKey: "knn_num"
  },
  {
    header: "Embedding Model",
    enableHiding: true,
    accessorKey: "embedding_model"
  },
  {
    header: "Inferencing LLM",
    enableHiding: true,
    accessorKey: "retrieval_model"
  },
  {
    header: "Inferencing LLM Temperature",
    enableHiding: true,
    accessorKey: "temp_retrieval_llm"
  },
  {
    header: "N Shot Prompts",
    enableHiding: true,
    accessorKey: "n_shot_prompts"
  },
  {
    header: "Directional Pricing",
    enableHiding: true,
    accessorKey: "directional_pricing"
  },
  {
    header: "Region",
    enableHiding: true,
    accessorKey: "region"
  },
  {
    header: "Rerank Model",
    enableHiding: true,
    accessorKey: "rerank_model_id"
  }
])

const columnVisibility = ref({
  select: props.selectable ?? false
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
          label: column.columnDef.header,
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
    <UTable ref="table" v-model:column-visibility="columnVisibility" sticky :columns="columns" :data="experiments"
      :loading="isLoading">
      <template #directional_pricing-cell="{ row }">
        {{ useHumanCurrencyAmount(row.original.directional_pricing) }}
      </template>
      <template #chunking_strategy-cell="{ row }">
        {{ useHumanChunkingStrategy(row.original.chunking_strategy) }}
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
    </UTable>
  </div>
</template>
