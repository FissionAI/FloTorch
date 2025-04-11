<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui';

const UButton = resolveComponent('UButton')
const UCheckbox = resolveComponent('UCheckbox')

const toast = useToast()

const modelValue = defineModel<ValidExperiment[]>()


const props = defineProps<{
  projectId: string
  experiments: ProjectExperiment[]
}>();

const table = useTemplateRef('table')

watchEffect(() => {
  if (table?.value?.tableApi && table.value.tableApi.getFilteredSelectedRowModel().rows) {
    modelValue.value = table.value.tableApi.getFilteredSelectedRowModel().rows.map((row: any) => {
      return row.original
    })
  }
})

const columns = ref<TableColumn<ProjectExperiment>[]>([
  {
    id: 'select',
    cell: ({ row }) => {
      if(row.original.experiment_status !== 'succeeded'){
        return null;
      }else {
        return h(UCheckbox, {
      'modelValue': row.getIsSelected(),
      'onUpdate:modelValue': (value: boolean) => {
        const selectedRows = table.value?.tableApi?.getFilteredSelectedRowModel().rows ?? [];
        if (value && (selectedRows.length > 2 && selectedRows.length < 3)) {
          toast.add({
            title: 'Min limit reached',
            description: `You can select atleast 2 experiments and atmost 3 experiments`,
            color: 'error'
          })
          return;
        }
        row.toggleSelected(!!value);
      },
          'ariaLabel': 'Select row'
        })
      }
    },
    enableHiding: false,
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
          color: "neutral",
          variant: "ghost",
          label: "Id",
          trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.id ?? 0;
      const b = rowB.original.id ?? 0;
      return a.localeCompare(b);
    },
    accessorKey: "id",
    enableHiding: false,
    label: 'Id',
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
          color: "neutral",
          variant: "ghost",
          label: "Status",
          trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    accessorKey: "experiment_status",
    enableHiding: true,
    label: 'Status',
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
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "config.retrieval_model",
    enableHiding: true,
    label: 'Inferencing Model',
    cell: ({ row }) => {
      return getModelName("retrieval", row.original.config.retrieval_model) || 'NA'
    },
    sortingFn: (rowA, rowB) => {
      const a = getModelName("retrieval", rowA.original.config.retrieval_model);
      const b = getModelName("retrieval", rowB.original.config.retrieval_model);
      return a?.localeCompare(b ?? '');
    }
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Estimated Cost",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "experiment_cost",
    enableHiding: true,
    label: 'Estimated Cost',
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.cost ?? 0;
      const b = rowB.original.cost ?? 0;
      return Number(a) - Number(b);
    },
    cell: ({ row }) => {
      return useHumanCurrencyAmount(useConvertStringToNumber(row.original.cost))
    }
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Faithfulness",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "eval_metrics.faithfulness_score",
    enableHiding: true,
    label: 'Faithfulness',
    sortingFn: (rowA, rowB) => {
      const getScore = (row: any) => {
        if ("faithfulness_score" in row.original.eval_metrics) {
          return row.original.eval_metrics.faithfulness_score ?? 0;
        }
        if ("M" in row.original.eval_metrics) {
          return row.original.eval_metrics.M?.faithfulness_score ?? 0;
        }
        return 0;
      };
      
      const a = getScore(rowA);
      const b = getScore(rowB);
      return Number(a) - Number(b);
    },
    cell: ({ row }) => {
      if(!row.original.config.knowledge_base){
        return "NA"

      }
      if ("faithfulness_score" in row.original.eval_metrics) {
        return row.original.eval_metrics.faithfulness_score ? parseFloat(row.original.eval_metrics.faithfulness_score.toString()).toFixed(2) : "-"
      }
      if ("M" in row.original.eval_metrics) {
        return row.original.eval_metrics.M?.faithfulness_score ? parseFloat(row.original.eval_metrics.M.faithfulness_score.toString()).toFixed(2) : "-"
      }
      return "-"
    }
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Context Precision",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "eval_metrics.context_precision_score",
    enableHiding: true,
    label: 'Context Precision',
    sortingFn: (rowA, rowB) => {
      if ("M" in rowA.original.eval_metrics) {
        const a = rowA.original.eval_metrics?.M?.context_precision_score;
        const b = rowB.original.eval_metrics?.M?.context_precision_score;
        return Number(a) - Number(b);
      }
      if ("context_precision_score" in rowA.original.eval_metrics) {
        const a = rowA.original.eval_metrics?.context_precision_score;
        const b = rowB.original.eval_metrics?.context_precision_score;
        return Number(a) - Number(b);
      }
      return 0;
    },
    cell: ({ row }) => {
       if(!row.original.config.knowledge_base){
        return "NA"

      }
      if ("context_precision_score" in row.original.eval_metrics) {
        return row.original.eval_metrics.context_precision_score ? parseFloat(row.original.eval_metrics.context_precision_score.toString()).toFixed(2) : "-"
      }
      if ("M" in row.original.eval_metrics) {
        return row.original.eval_metrics.M?.context_precision_score ? parseFloat(row.original.eval_metrics.M.context_precision_score.toString()).toFixed(2) : "-"
      }
      return "-"
    }
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Maliciousness",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    label: 'Maliciousness',
    accessorKey: "eval_metrics.aspect_critic_score",
    enableHiding: true,
    sortingFn: (rowA, rowB) => {
      if ("M" in rowA.original.eval_metrics) {
        const a = rowA.original.eval_metrics?.M?.aspect_critic_score ?? 0;
        const b = rowB.original.eval_metrics?.M?.aspect_critic_score ?? 0;
        return Number(a) - Number(b);
      }
      if ("aspect_critic_score" in rowA.original.eval_metrics) {
        const a = rowA.original.eval_metrics?.aspect_critic_score ?? 0;
        const b = rowB.original.eval_metrics?.aspect_critic_score ?? 0;
        return Number(a) - Number(b);
      }
      return 0;
    },
    cell: ({ row }) => {
      if ("aspect_critic_score" in row.original.eval_metrics) {
        return row.original.eval_metrics.aspect_critic_score ? parseFloat(row.original.eval_metrics.aspect_critic_score.toString()).toFixed(2) : "-"
      }
      if ("M" in row.original.eval_metrics) {
        return row.original.eval_metrics.M?.aspect_critic_score ? parseFloat(row.original.eval_metrics.M.aspect_critic_score.toString()).toFixed(2) : "-"
      }
      return "-"
    }
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Answer Relevancy",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "eval_metrics.answers_relevancy_score",
    enableHiding: true,
    label: 'Answer Relevancy',
    sortingFn: (rowA, rowB) => {
      if ("M" in rowA.original.eval_metrics) {
        const a = rowA.original.eval_metrics?.M?.answers_relevancy_score ?? 0;
        const b = rowB.original.eval_metrics?.M?.answers_relevancy_score ?? 0;
        return Number(a) - Number(b);
      }
      if ("answers_relevancy_score" in rowA.original.eval_metrics) {
        const a = rowA.original.eval_metrics?.answers_relevancy_score ?? 0;
        const b = rowB.original.eval_metrics?.answers_relevancy_score ?? 0;
        return Number(a) - Number(b);
      }
      return 0;
    },
    cell: ({ row }) => {
      if ("answers_relevancy_score" in row.original.eval_metrics) {
        return row.original.eval_metrics.answers_relevancy_score ? parseFloat(row.original.eval_metrics.answers_relevancy_score.toString()).toFixed(2) : "-"
      }
      if ("M" in row.original.eval_metrics) {
        return row.original.eval_metrics.M?.answers_relevancy_score ? parseFloat(row.original.eval_metrics.M.answers_relevancy_score.toString()).toFixed(2) : "-"
      }
      return "-"
    }
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Duration",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "experiment_duration",
    enableHiding: true,
    label: 'Duration',
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.total_time ?? 0;
      const b = rowB.original.total_time ?? 0;
      return Number(a) - Number(b);
    },
    cell: ({ row }) => {
      return row.original.total_time && (row.original.experiment_status === 'succeeded' || row.original.experiment_status === 'failed') ? useHumanDuration(row.original.total_time) : "-"
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
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "config.embedding_model",
    enableHiding: true,
    label: 'Embedding Model',
    cell: ({ row }) => {
      return getModelName("indexing", row.original.config.embedding_model) || 'NA'
    }
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
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "config.eval_service",
    enableHiding: true,
    label: 'Evaluation Service',
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.config?.eval_service ?? 0;
      const b = rowB.original.config?.eval_service ?? 0;
      return a.localeCompare(b);
    },
    cell: ({ row }) => {
      return row.original.config?.eval_service ? row.original.config.eval_service : "-"
    }
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
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "config.eval_embedding_model",
    enableHiding: true,
    label: 'Evaluation Embedding Model',
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.config?.eval_embedding_model ?? 0;
      const b = rowB.original.config?.eval_embedding_model ?? 0;
      return a.localeCompare(b);
    },
    cell: ({ row }) => {
      return row.original.config?.eval_embedding_model ? row.original.config.eval_embedding_model : "-"
    }
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
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "config.eval_retrieval_model",
    enableHiding: true,
    label: 'Evaluation Inferencing Model',
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.config?.eval_retrieval_model ?? 0;
      const b = rowB.original.config?.eval_retrieval_model ?? 0;
      return a.localeCompare(b);
    },
    cell: ({ row }) => {
      return row.original.config?.eval_retrieval_model ? row.original.config.eval_retrieval_model : "-"
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
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "directional_pricing",
    enableHiding: true,
    label: 'Directional Cost',
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.config?.directional_pricing ?? 0;
      const b = rowB.original.config?.directional_pricing ?? 0;
      return Number(a) - Number(b);
    },
    cell: ({ row }) => {
      return row.original.config?.directional_pricing ? useHumanCurrencyAmount(row.original.config?.directional_pricing) : "-"
    }
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
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "config.indexing_algorithm",
    enableHiding: true,
    label: 'Indexing Algorithm',
    cell: ({ row }) => {
      return useHumanIndexingAlgorithm(row.original.config.indexing_algorithm) || 'NA'
    }
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
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "config.chunking_strategy",
    enableHiding: true,
    label: 'Chunking',
    cell: ({ row }) => {
      return useHumanChunkingStrategy(row.original.config.chunking_strategy) || 'NA'
    },
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
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "config.temp_retrieval_llm",
    enableHiding: true,
    label: 'Inferencing Model Temperature',
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.config?.temp_retrieval_llm ?? 0;
      const b = rowB.original.config?.temp_retrieval_llm ?? 0;
      return Number(a) - Number(b);
    }
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
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "config.rerank_model_id",
    enableHiding: true,
    label: 'Reranking Model',
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.config.rerank_model_id ?? 0;
      const b = rowB.original.config.rerank_model_id ?? 0;
      return a.localeCompare(b);
    },
    cell: ({ row }) => {
      return row.original.config.rerank_model_id.includes('none') && row.original.config.knowledge_base !== true ? 'NA' : row.original.config.rerank_model_id
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
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "config.guardrail_name",
    enableHiding: true,
    label: 'Guardrail',
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.config?.guardrail_name ?? 0;
      const b = rowB.original.config?.guardrail_name ?? 0;
      return a.localeCompare(b);
    },
    cell: ({ row }) => {
      return row.original.config?.guardrail_name ? row.original.config.guardrail_name : "NA"
    }
  },
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
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "config.kb_name",
    enableHiding: true,
    label: 'Bedrock Kb Name',
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.config?.kb_name ?? 0;
      const b = rowB.original.config?.kb_name ?? 0;
      return a.localeCompare(b);
    },
    cell: ({ row }) => {
      return row.original.config?.kb_name ? row.original.config.kb_name : "NA"
    }
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
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
        h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
      ]);
    },
    accessorKey: "config.knn",
    enableHiding: true,
    label: 'KNN',
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.config?.knn_num ?? 0;
      const b = rowB.original.config?.knn_num ?? 0;
      return a - b;
    },
    cell: ({ row }) => {
      return row.original.config?.knn_num !== true && row.original.config?.knn_num === 0 ? "NA" : row.original.config.knn_num;
    }
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
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    enableHiding: true,
    accessorKey: "config.n_shot_prompts",
    label: 'N Shot Prompts',
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h('div', { class: 'flex items-center justify-between' }, [
        h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Scores",
        trailingIcon: isSorted
          ? isSorted === "asc"
            ? "i-lsicon:triangle-up-filled"
            : "i-lsicon:triangle-down-filled"
          : "i-lsicon:triangle-down-outline",
     class: "-mx-2.5 focus:font-bold hover:font-bold",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      }),
      h('div', { class: 'h-5 w-[2px] bg-gray-200 dark:bg-gray-700 ml-2' })
    ]);
    },
    cell: ({ row }) => {
      return 'scores' in row.original && (row.original.scores !== 0 || Object.keys(row.original.scores).length === 0) ? row.original.scores : "NA"
    },
    enableHiding: true,
    accessorKey: "scores",
    label: 'Scores',
  },
])

const navigateToExperiment = (experimentId: string) => {
  window.location.href = `/projects/${props.projectId}/experiments/${experimentId}`
}

const getModelName = (type: "indexing" | "retrieval", model: string) => {
  return useGetModelData(type, model)?.label
}

const hasAllExperimentsCompleted = computed(() => {
  return props?.experiments?.every((experiment) => {
    return experiment.experiment_status === "succeeded" || experiment.experiment_status === "failed"
  })
})

const openTooltipId = ref<string | null>(null)



const navigateHumanEvaluation = () => {
  const experimentIds = modelValue.value?.map(experiment => experiment.id).join(',')
  navigateTo(`/projects/${props.projectId}/humanevaluation?experiments=${experimentIds}`);
}



const columnVisibility = ref({
  config_knn: false,
  config_n_shot_prompts: false,
  directional_pricing: false,
  config_kb_name: false,
  config_guardrail_name: false,
  config_eval_service: false,
  config_eval_embedding_model: false,
  config_eval_retrieval_model: false,
  config_rerank_model_id: false,
  config_temp_retrieval_llm: false,
  config_indexing_algorithm: false,
  config_chunking_strategy: false,
  config_embedding_model: false,
  scores: false,
  
})

const sorting = ref([
  {
    id: "id",
    asc: true,
  },
]);


</script>

<template>
  <div class="space-y-3">
    <div class="flex justify-between">
      <p><span class="font-medium">Region:</span> {{ experiments?.[0]?.config?.region }}</p>
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
    <UTable class="h-100" sticky v-model:column-visibility="columnVisibility" v-model:sorting="sorting" ref="table" :columns="columns" :data="experiments">
       <template #empty>
        <div  class="flex flex-col items-center justify-center py-6">
          <p class="text-gray-500">No experiments found...!</p>
        </div>
      </template>
      <template #id-cell="{ row }">
        <a 
          href="#"
          class="text-blue-500 hover:text-black hover:underline"
          @click.prevent="navigateToExperiment(row.original.id)"
        >
          {{ row.original.id }}
        </a>
      </template>
      <template #temp_retrieval_llm-cell="{ row }">
        {{ row.original.config?.temp_retrieval_llm ? row.original.config.temp_retrieval_llm : "-" }}
      </template>
      <template #experiment_status-cell="{ row }">
        <!-- <UBadge variant="subtle" :color="useExperimentStatusColor(row.original.experiment_status)"> -->
        <div :class="`${useExperimentBadgeColor(row.original.experiment_status)}-badge w-min-[150px]`" class="flex items-center gap-2">
          <UIcon :name="useExperimentBadgeIcon(row.original.experiment_status)" />
          {{ useHumanExperimentStatus(row.original.experiment_status) }}
        </div>
          <!-- <template #leading>
            <UIcon :name="useExperimentStatusIcon(row.original.experiment_status)" />
          </template>
          {{ useHumanExperimentStatus(row.original.experiment_status) }} -->
        <!-- </UBadge> -->
      </template>
      <template #directional_pricing-cell="{row}">     
        <div class="w-full">
          <UTooltip 
            :open="openTooltipId === row.original.id"
            :key="row.original.id" 
            :content="{side: 'right'}"
            class="h-full"
          >
            <a 
              @click="openTooltipId = openTooltipId === row.original.id ? null : row.original.id" 
              class="underline decoration-dotted" 
              href="#"
            >
              {{useHumanCurrencyAmount(row.original?.config?.directional_pricing)}}
            </a>
            <template #content>
                  <div>
              <UButton @click="openTooltipId = null" variant="ghost" color="neutral" trailing-icon="i-lucide-x" />

                    <ul>
                      <li class="mb-2"><span class="tooltip-text-grey">Indexing Cost Estimate:</span> {{useHumanCurrencyAmount(row.original.indexing_cost_estimate,3)}}</li>
                      <li class="mb-2"><span class="tooltip-text-grey">Retrieval Cost Estimate:</span> {{useHumanCurrencyAmount(row.original.retrieval_cost_estimate,3)}}</li>
                      <li class="mb-2"><span class="tooltip-text-grey">Inferencing Cost Estimate:</span> {{useHumanCurrencyAmount(row.original.inferencing_cost_estimate,3)}}</li>
                      <li class="mb-2"><span class="tooltip-text-grey">Evaluation Cost Estimate:</span> {{useHumanCurrencyAmount(row.original.eval_cost_estimate,3)}}</li>
                    </ul>
                  </div>
              </template>
          </UTooltip>
        </div>
      </template>
    </UTable>
    <div v-if="hasAllExperimentsCompleted" class="flex justify-end">
      <UButton :disabled="modelValue && (modelValue.length <= 1 || modelValue.length > 3)" class="secondary-btn mr-2" @click="navigateHumanEvaluation">{{modelValue && modelValue.length > 1 ? 'Human Evaluation': 'Choose 2-3 experiments for Human Evaluation'}}</UButton>
      <DownloadResultsButton :results="experiments" :question-metrics="false" button-label="Download Results" />
    </div>
  </div>
</template>
