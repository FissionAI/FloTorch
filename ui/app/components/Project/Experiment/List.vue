<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui';

const UButton = resolveComponent('UButton')
const props = defineProps<{
  projectId: string
  experiments: ProjectExperiment[]
}>();

const table = useTemplateRef('table')

const columns = ref<TableColumn<ProjectExperiment>[]>([
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "ID",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    label: "ID",
    accessorKey: "id",
    enableHiding: false,
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
    label: "Embedding Model",
    accessorKey: "config.embedding_model",
    enableHiding: true,
    cell: ({ row }) => {
      return getModelName("indexing", row.original.config.embedding_model)
    }
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
    label: "Inferencing Model",
    accessorKey: "config.retrieval_model",
    enableHiding: true,
    cell: ({ row }) => {
      return getModelName("retrieval", row.original.config.retrieval_model)
    }
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
    label: "Indexing Algorithm",
    accessorKey: "config.indexing_algorithm",
    enableHiding: true,
    cell: ({ row }) => {
      return useHumanIndexingAlgorithm(row.original.config.indexing_algorithm)
    }
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
    accessorKey: "config.chunking_strategy",
    enableHiding: true,
    cell: ({ row }) => {
      return useHumanChunkingStrategy(row.original.config.chunking_strategy)
    },
    label: "Chunking"
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Status",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    label: "Status",
    accessorKey: "experiment_status",
    enableHiding: true,
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
    label: "Inferencing Model Temperature",
    accessorKey: "config.temp_retrieval_llm",
    enableHiding: true,
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.config?.temp_retrieval_llm ?? 0;
      const b = rowB.original.config?.temp_retrieval_llm ?? 0;
      return Number(a) - Number(b);
    }
  },
  {
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Faithfulness",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    label: 'Faithfulness',
    accessorKey: "eval_metrics.faithfulness_score",
    enableHiding: true,
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
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Context Precision",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    label: 'Context Precision',
    accessorKey: "eval_metrics.context_precision_score",
    enableHiding: true,
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.eval_metrics?.context_precision_score ?? 0;
      const b = rowB.original.eval_metrics?.context_precision_score ?? 0;
      return Number(a) - Number(b);
    },
    cell: ({ row }) => {
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
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Aspect Critic",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    label: 'Aspect Critic',
    accessorKey: "eval_metrics.aspect_critic_score",
    enableHiding: true,
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.eval_metrics?.aspect_critic_score ?? 0;
      const b = rowB.original.eval_metrics?.aspect_critic_score ?? 0;
      return Number(a) - Number(b);
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
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Answers Relevancy",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    label: 'Answers Relevancy',
    accessorKey: "eval_metrics.answers_relevancy_score",
    enableHiding: true,
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.eval_metrics?.answers_relevancy_score ?? 0;
      const b = rowB.original.eval_metrics?.answers_relevancy_score ?? 0;
      return Number(a) - Number(b);
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
    label: 'Evaluation Service',
    accessorKey: "config.eval_service",
    enableHiding: true,
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
    label: 'Evaluation Embedding Model',
    accessorKey: "config.eval_embedding_model",
    enableHiding: true,
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
    label: 'Evaluation Retrieval Model',
    accessorKey: "config.eval_retrieval_model",
    enableHiding: true,
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
    label: 'Directional Pricing',
    accessorKey: "directional_pricing",
    enableHiding: true,
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
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Duration",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    label: 'Duration',
    accessorKey: "experiment_duration",
    enableHiding: true,
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
      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Estimated Cost",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    label: 'Estimated Cost',
    accessorKey: "experiment_cost",
    enableHiding: true,
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.cost ?? 0;
      const b = rowB.original.cost ?? 0;
      return Number(a) - Number(b);
    },
    cell: ({ row }) => {
      return row.original.cost? useHumanCurrencyAmount(row.original.cost) : "-"
    }
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
    label: 'Reranking Model',
    accessorKey: "rerank_model_id",
    enableHiding: true,
    sortingFn: (rowA, rowB) => {
      const a = rowA.original.rerank_model_id ?? 0;
      const b = rowB.original.rerank_model_id ?? 0;
      return a.localeCompare(b);
    },
    cell: ({ row }) => {
      return row.original.rerank_model_id? row.original.rerank_model_id : "-"
    }
  }
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

const columnVisibility = ref({
  directional_pricing: false,
})
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
    <UTable class="h-100" sticky v-model:column-visibility="columnVisibility" ref="table" :columns="columns" :data="experiments">
      <template #id-cell="{ row }">
        <a 
          href="#"
          class="text-blue-500 hover:underline"
          @click.prevent="navigateToExperiment(row.original.id)"
        >
          {{ row.original.id }}
        </a>
      </template>
      <template #temp_retrieval_llm-cell="{ row }">
        {{ row.original.config?.temp_retrieval_llm ? row.original.config.temp_retrieval_llm : "-" }}
      </template>
      <template #experiment_status-cell="{ row }">
        <UBadge variant="subtle" :color="useExperimentStatusColor(row.original.experiment_status)">
          <template #leading>
            <UIcon :name="useExperimentStatusIcon(row.original.experiment_status)" />
          </template>
          {{ useHumanExperimentStatus(row.original.experiment_status) }}
        </UBadge>
      </template>
      <template #directional_pricing-cell="{row}">     
        <div class="w-full">
            <UTooltip   :content="{side: 'right'}">
                    <a class="text-blue-500 hover:underline" href="#">{{row.original?.config?.directional_pricing}}</a>
                    <template #content>
                      <UCard class="w-full">
                        <table class="w-full">
                          <tbody>
                            <tr>
                              <td>Indexing Cost :</td>
                              <td>{{useHumanCurrencyAmount(row.original?.config?.indexing_cost_estimate)}}</td>
                            </tr>
                            <tr>
                              <td>Retrieval Cost :</td>
                              <td>{{useHumanCurrencyAmount(row.original?.config?.retrieval_cost_estimate)}}</td>
                            </tr>
                            <tr>
                              <td>Evaluation Cost :</td>
                              <td>{{useHumanCurrencyAmount(row.original?.config?.eval_cost_estimate)}}</td>
                            </tr>
                          </tbody>
                        </table>
                      </UCard>
                  </template>
            </UTooltip>
          </div>
      </template>
    </UTable>
    <div v-if="hasAllExperimentsCompleted" class="flex justify-end">
      <DownloadResultsButton :results="experiments" :question-metrics="false" button-label="Download Results" />
    </div>
  </div>
</template>
