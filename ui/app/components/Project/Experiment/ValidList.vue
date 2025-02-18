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
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Chunking",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "chunking_strategy",
    label: 'Chunking',
    sortingFn: (rowA, rowB) => {
      const getChunkingValue = (row: any) => {
        const strategy = useHumanChunkingStrategy(row.chunking_strategy);
        if (!strategy) return 'NA';
        if (strategy === 'Hierarchical') {
          return row.hierarchical_child_chunk_size && row.hierarchical_parent_chunk_size
            ? `${row.hierarchical_child_chunk_size}-${row.hierarchical_parent_chunk_size}`
            : 'NA';
        }
        return strategy;
      };
      
      const a = getChunkingValue(rowA.original);
      const b = getChunkingValue(rowB.original);
      return a.localeCompare(b);
    }
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Embedding Model",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "embedding_model",
    label: 'Embedding Model',
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "N Shot Prompts",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "n_shot_prompts",
    label: 'N Shot Prompts',
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "KNN",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "knn_num",
    label: 'KNN',
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Reranking Model",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "rerank_model_id",
    label: 'Reranking Model',
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Inferencing Model",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "retrieval_model",
    label: 'Inferencing Model',
    sortingFn: (rowA, rowB) => {
      const a = useModelName("retrieval", rowA.original.retrieval_model);
      const b = useModelName("retrieval", rowB.original.retrieval_model);
      return a.localeCompare(b);
    }
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Guardrail",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "guardrail_name",
    label: 'Guardrail',
    cell: ({ row }) => {
      return row.original.guardrail_name || 'NA';
    }
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Directional Cost",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "directional_pricing",
    label: 'Directional Cost',
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Chunk Size",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "chunk_size",
    label: 'Chunk Size',
    sortingFn: (rowA, rowB) => {
      const getChunkSizeValue = (row: any) => {
        const strategy = useHumanChunkingStrategy(row.chunking_strategy);
        if (strategy === 'Hierarchical') {
          // For hierarchical, create a composite value using both sizes
          const childSize = Number(row.hierarchical_child_chunk_size ?? 0);
          const parentSize = Number(row.hierarchical_parent_chunk_size ?? 0);
          // Multiply parent by 1000 to ensure it takes precedence in sorting
          return (parentSize * 1000) + childSize;
        }
        return Number(row.chunk_size ?? 0);
      };

      const a = getChunkSizeValue(rowA.original);
      const b = getChunkSizeValue(rowB.original);
      return a - b;
    }
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Chunk Overlap Percentage",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "chunk_overlap",
    label: 'Chunk Overlap Percentage',
    sortingFn: (rowA, rowB) => {
      const getOverlapValue = (row: any) => {
        const strategy = useHumanChunkingStrategy(row.chunking_strategy);
        return strategy === 'Fixed' 
          ? Number(row.chunk_overlap ?? 0)
          : Number(row.hierarchical_chunk_overlap_percentage ?? 0);
      };
      
      const a = getOverlapValue(rowA.original);
      const b = getOverlapValue(rowB.original);
      return a - b;
    }
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Vector Dimensions",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "vector_dimension",
    label: 'Vector Dimensions',
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Indexing Algorithm",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "indexing_algorithm",
    label: 'Indexing Algorithm',
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Inferencing Model Temperature",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "temp_retrieval_llm",
    label: 'Inferencing Model Temperature',
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Evaluation Service",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "eval_service",
    label: 'Evaluation Service',
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Evaluation Embedding Model",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "eval_embedding_model",
    label: 'Evaluation Embedding Model',
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Evaluation Inferencing Model",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "eval_retrieval_model",
    label: 'Evaluation Inferencing Model',
  },
  // {
  //   header: ({ column }) => {
  //     const isSorted = column.getIsSorted();
  //     return h(UButton, {
  //       color: "neutral",
  //       variant: "ghost",
  //       label: "Region",
  //       icon: isSorted
  //         ? isSorted === "asc"
  //           ? "i-lucide-arrow-up-narrow-wide"
  //           : "i-lucide-arrow-down-wide-narrow"
  //         : "i-lucide-arrow-up-down",
  //       class: "-mx-2.5",
  //       onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
  //     });
  //   },
  //   enableHiding: true,
  //   accessorKey: "region",
  //   label: "Region"
  // },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Bedrock Kb Name",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-outline"
            : "i-lsicon:triangle-down-outline"
          : "i-lsicon:triangle-down-outline",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "kb_name",
    label: 'Bedrock Kb Name',
    cell: ({ row }) => {
      return row.original.kb_name ? row.original.kb_name : 'NA';
    }
  }
])

const columnVisibility = ref({
  select: props.selectable ?? false,
  // region: false,
  // rerank_model_id: false,
  eval_retrieval_model: false,
  eval_embedding_model: false,
  eval_service:false,
  indexing_algorithm: false,
  temp_retrieval_llm: false,
  chunk_overlap : false,
  kb_name : false,
  // guardrail_name: false,
  // knn_num : false,
  // n_shot_prompts : false,
  vector_dimension : false,
  chunk_size : false
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
      <template #empty>
        <div class="flex flex-col items-center justify-center py-6">
          <p v-if="isLoading" class="text-gray-500">Please wait, we are fetching valid experiments...!</p>
          <p v-else>No valid experiments are found...!</p>
        </div>
      </template>
      <template #directional_pricing-cell="{ row }">
        <div class="w-full">
              <UTooltip   :content="{side: 'right'}">
                <a class="text-blue-500 hover:underline" href="#">{{useHumanCurrencyAmount(row.original.directional_pricing)}}</a>
                <template #content>
                  <UCard class="w-full">
                    <table class="w-full">
                      <tbody>
                        <tr>
                          <td>Indexing Cost Estimate:</td>
                          <td>{{useHumanCurrencyAmount(row.original.indexing_cost_estimate,3)}}</td>
                        </tr>
                        <tr>
                          <td>Retrieval Cost Estimate:</td>
                          <td>{{useHumanCurrencyAmount(row.original.retrieval_cost_estimate,3)}}</td>
                        </tr>
                        <tr>
                          <td>Inferencing Cost Estimate:</td>
                          <td>{{useHumanCurrencyAmount(row.original.inferencing_cost_estimate,3)}}</td>
                        </tr>
                        <tr>
                          <td>Evaluation Cost Estimate:</td>
                          <td>{{useHumanCurrencyAmount(row.original.eval_cost_estimate,3)}}</td>
                        </tr>
                         
                      </tbody>
                    </table>
                  </UCard>
              </template>
              </UTooltip>
        </div>
      </template>
      <template #vector_dimension-cell="{ row }">
        <span class=" ">
          {{ row.original.vector_dimension || 'NA' }}
        </span>
      </template>
      <template #n_shot_prompts-cell="{ row }">
        <span class=" ">
          {{ row.original.n_shot_prompts !=='' ? row.original.n_shot_prompts : 'NA' }}
        </span>
      </template>
      <template #temp_retrieval_llm-cell="{ row }">
        <span class=" ">
          {{ row.original.temp_retrieval_llm || 'NA' }}
        </span>
      </template>
      <template #chunking_strategy-cell="{ row }">
        {{ useHumanChunkingStrategy(row.original.chunking_strategy) || 'NA' }}
      </template>
      <template #chunk_size-cell="{ row }">
        <span>
          {{ row.original.chunking_strategy ?  useHumanChunkingStrategy(row.original.chunking_strategy) === 'Fixed' ? row.original.chunk_size : [row.original.hierarchical_child_chunk_size, row.original.hierarchical_parent_chunk_size] : 'NA' }}
        </span>
      </template>
       <template #chunk_overlap-cell="{ row }">
       <span class=" ">
          {{ row.original.chunking_strategy ?  useHumanChunkingStrategy(row.original.chunking_strategy) === 'Fixed' ? row.original.chunk_overlap : row.original.hierarchical_chunk_overlap_percentage : 'NA'}}
          </span>
      </template>
      <template #indexing_algorithm-cell="{ row }">
        {{ useHumanIndexingAlgorithm(row.original.indexing_algorithm) || 'NA' }}
      </template>
      <template #embedding_model-cell="{ row }">
        {{ useModelName("indexing", row.original.embedding_model) || 'NA' }}
      </template>
      <template #retrieval_model-cell="{ row }">
        {{ useModelName("retrieval", row.original.retrieval_model) || 'NA' }}
      </template>
       <template #kb_name-cell="{row}">
      {{!row.original.bedrock_knowledge_base ? 'NA' : row.original.kb_name}}
      </template>
      <template #rerank_model_id-cell="{row}">
        {{row.original.knowledge_base !== true && row.original.rerank_model_id.includes('none') ? 'NA' : row.original.rerank_model_id}}
      </template>
      <template #knn_num-cell="{row}">
        {{ row.original.knowledge_base !== true && row.original.knn_num === 0 ? 'NA' : row.original.knn_num }}
      </template>
    </UTable>
  </div>
</template>

<style scoped>
span.truncate {
  white-space: pre-wrap !important;
  word-break: break-word !important;
}
</style>
