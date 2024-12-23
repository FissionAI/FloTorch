import type {
  ProjectExperimentStatus,
  ProjectStatus,
} from "~~/shared/types/projects.type";

export const useHumanDateTime = (date: string) => {
  return Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
    hour12: true,
  }).format(new Date(date));
};

export const useHumanProjectStatus = (
  status?: ProjectStatus,
  defaultString?: string
) => {
  switch (status) {
    case "not_started":
      return "Not Started";
    case "in_progress":
      return "In Progress";
    case "completed":
      return "Completed";
    case "failed":
      return "Failed";
    default:
      return defaultString || status || "Unknown";
  }
};

export const useHumanExperimentStatus = (
  status?: ProjectExperimentStatus,
  defaultString?: string
) => {
  switch (status) {
    case "not_started":
      return "Not Started";
    case "in_progress":
      return "In Progress";
    case "indexing_inprogress":
      return "Indexing in Progress";
    case "indexing_completed":
      return "Indexing Completed";
    case "retrieval_inprogress":
      return "Retrieval in Progress";
    case "retrieval_completed":
      return "Retrieval Completed";
    case "eval_inprogress":
      return "Evaluation in Progress";
    case "eval_completed":
      return "Evaluation Completed";
    case "failed":
      return "Failed";
    case "succeeded":
      return "Completed";
    default:
      return defaultString || status || "Unknown";
  }
};

export const useProjectCreateMeta = () => {
  return {
    dataStrategy: {
      regions: [
        {
          label: "us-east-1 (Virginia)",
          value: "us-east-1",
        },
        {
          label: "us-west-2 (Oregon)",
          value: "us-west-2",
        },
      ],
    },
    indexingStrategy: {
      chunkingStrategy: [
        {
          label: "Fixed",
          value: "fixed",
        },
        {
          label: "Hierarchical (Coming Soon)",
          value: "hierarchical",
          disabled: true,
        },
      ],
      chunkSize: [
        {
          label: "128",
          value: 128,
        },
        {
          label: "256",
          value: 256,
        },
        {
          label: "512",
          value: 512,
        },
      ],
      chunkOverlapPercentage: [
        {
          label: "5",
          value: 5,
        },
        {
          label: "10",
          value: 10,
        },
        {
          label: "15",
          value: 15,
        },
        {
          label: "20",
          value: 20,
        },
      ],
      embeddingService: [
        {
          type: "label",
          label: "Bedrock",
        },
        // {
        //   label: "Titan Embeddings - Text",
        //   value: "amazon.titan-embed-text-v1",
        //   service: "bedrock",
        // },
        {
          label: "Titan Embeddings V2 - Text",
          value: "amazon.titan-embed-text-v2:0",
          service: "bedrock",
        },
        {
          label: "Titan Multimodal embeddings G1",
          value: "amazon.titan-embed-image-v1",
          service: "bedrock",
        },
        {
          label: "Cohere Embed English",
          value: "cohere.embed-english-v3",
          service: "bedrock",
        },
        {
          label: "Cohere Embed Multilingual",
          value: "cohere.embed-multilingual-v3",
          service: "bedrock",
        },
        {
          type: "label",
          label: "SageMaker",
        },
        {
          label: "BAAI/bge-large-en-v1.5 (Coming Soon)",
          value: "BAAI/bge-large-en-v1.5",
          service: "sagemaker",
          disabled: true,
        },
      ],
      vectorDimensions: [
        {
          label: "256",
          value: 256,
        },
        {
          label: "384",
          value: 384,
        },
        {
          label: "512",
          value: 512,
        },
        {
          label: "1024",
          value: 1024,
        },
      ],
      indexingAlgorithms: [
        {
          label: "HNSW",
          value: "hnsw",
        },
        {
          label: "HNSW - BQ",
          value: "hnsw_bq"
        },
        {
          label: "HNSW - SQ",
          value: "hnsw_sq"
        },
      ],
    },
    retrievalStrategy: {
      shotPrompts: [
        {
          label: "0",
          value: 0,
        },
        {
          label: "1",
          value: 1,
        },
        {
          label: "2",
          value: 2,
        },
        {
          label: "3",
          value: 3,
        },
      ],
      knnNumber: [
        {
          label: "3",
          value: 3,
        },
        {
          label: "5",
          value: 5,
        },
        {
          label: "10",
          value: 10,
        },
        {
          label: "15",
          value: 15,
        },
      ],
      llmService: [
        {
          type: "label",
          label: "Bedrock",
        },
        {
          label: "Amazon Titan Text G1 - Lite",
          value: "amazon.titan-text-lite-v1",
          service: "bedrock",
        },
        {
          label: "Amazon Titan Text G1 - Express",
          value: "amazon.titan-text-express-v1",
          service: "bedrock",
        },
        {
          label: "Amazon Nova Lite V1",
          value: "amazon.nova-lite-v1:0",
          service: "bedrock",
        },
        {
          label: "Amazon Nova Micro V1",
          value: "amazon.nova-micro-v1:0",
          service: "bedrock",
        },
        {
          label: "Amazon Nova Pro V1",
          value:"amazon.nova-pro-v1:0",
          service: "bedrock",
        },
        {
          label: "Claude 3.5 Sonnet v2",
          value: "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
          service: "bedrock",
        },
        {
          label: "Claude 3.5 Sonnet",
          value: "anthropic.claude-3-5-sonnet-20240620-v1:0",
          service: "bedrock",
        },
        {
          label: "Cohere Command R+",
          value: "cohere.command-r-plus-v1:0",
          service: "bedrock",
        },
        {
          label: "Cohere Command R",
          value: "cohere.command-r-v1:0",
          service: "bedrock",
        },
        {
          label: "Meta Llama 3.2 1B Instruct",
          value: "us.meta.llama3-2-1b-instruct-v1:0",
          service: "bedrock",
        },
        {
          label: "Meta Llama 3.2 3B Instruct",
          value: "us.meta.llama3-2-3b-instruct-v1:0",
          service: "bedrock",
        },
        {
          label: "Meta Llama 3.2 11B Vision Instruct",
          value: "us.meta.llama3-2-11b-instruct-v1:0",
          service: "bedrock",
        },
        {
          label: "Meta Llama 3.2 90B Vision Instruct",
          value: "us.meta.llama3-2-90b-instruct-v1:0",
          service: "bedrock",
        },
        {
          label: "Mistral 7B Instruct",
          value: "mistral.mistral-7b-instruct-v0:2",
          service: "bedrock",
        },
        {
          label: "Mistral Large",
          value: "mistral.mistral-large-2402-v1:0",
          service: "bedrock",
        },
        {
          type: "label",
          label: "SageMaker",
        },
        {
          label: "Qwen/Qwen2.5-32B-Instruct (Coming Soon)",
          value: "Qwen/Qwen2.5-32B-Instruct",
          service: "sagemaker",
          disabled: true,
        },
        {
          label: "Qwen/Qwen2.5-14B-Instruct (Coming Soon)",
          value: "Qwen/Qwen2.5-14B-Instruct",
          service: "sagemaker",
          disabled: true,
        },
        {
          label: "Meta-Llama/Llama-3.1-8B (Coming Soon)",
          value: "Meta-Llama/Llama-3.1-8B",
          service: "sagemaker",
          disabled: true,
        },
        {
          label: "Meta-Llama/Llama-3.1-70B-Instruct (Coming Soon)",
          value: "Meta-Llama/Llama-3.1-70B-Instruct",
          service: "sagemaker",
          disabled: true,
        },
      ],
      temperature: [
        {
          label: "0",
          value: 0,
        },
        {
          label: "0.3",
          value: 0.3,
        },
        {
          label: "0.5",
          value: 0.5,
        },
        {
          label: "0.7",
          value: 0.7,
        },
      ],
    },
  };
};

const generateId = () => {
  return (
    Math.random().toString(36).substring(2, 15) +
    Math.random().toString(36).substring(2, 15)
  );
};

export const useProjectUploadConfigState = createGlobalState(() => {
  const projectUploadConfig = ref<Record<string, Record<string, any>>>({});
  return { projectUploadConfig };
});

export const useGetModelData = (
  type: "indexing" | "retrieval",
  modelValue: string
) => {
  const meta = useProjectCreateMeta();
  if (type === "indexing") {
    const model = meta.indexingStrategy.embeddingService.find(
      (m) => m.value === modelValue
    );
    return model;
  }
  const model = meta.retrievalStrategy.llmService.find(
    (m) => m.value === modelValue
  );
  return model;
};

export const useModelName = (type: "indexing" | "retrieval", model: string) => {
  return useGetModelData(type, model)?.label?.replace(" (Coming Soon)", "");
};

export const useProjectUploadConfig = () => {
  const state = useProjectUploadConfigState();

  const createConfig = (config: Record<string, any>) => {
    const id = generateId();
    state.projectUploadConfig.value[id] = {
      prestep: {
        ...config.prestep,
        name: config.name,
        kb_data: undefined,
        gt_data: undefined,
      },
      indexing: {
        ...config.indexing,
        embedding: config.indexing?.embedding?.map((pc: any) => {
          return useGetModelData("indexing", pc.model);
        }),
      },
      retrieval: {
        ...config.retrieval,
        retrieval: config.retrieval?.retrieval?.map((pc: any) => {
          return useGetModelData("retrieval", pc.model);
        }),
      },
    };
    return id;
  };

  const getConfig = (id?: string) => {
    return id ? state.projectUploadConfig.value[id] : undefined;
  };

  return {
    projectUploadConfig: state.projectUploadConfig,
    createConfig,
    getConfig,
  };
};

export const useProjectStatusColor = (status: ProjectStatus) => {
  if (status === "not_started") {
    return "neutral";
  } else if (status === "in_progress") {
    return "info";
  } else if (status === "completed") {
    return "success";
  } else if (status === "failed") {
    return "error";
  }
  return "neutral";
};

export const useProjectStatusIcon = (status: ProjectStatus) => {
  if (status === "in_progress") {
    return "i-lucide-loader";
  } else if (status === "completed") {
    return "i-lucide-check";
  } else if (status === "not_started") {
    return "i-lucide-clock-alert";
  } else if (status === "failed") {
    return "i-lucide-x";
  }
  return "i-lucide-circle-alert";
};

export const useExperimentStatusIcon = (status: ProjectExperimentStatus) => {
  if (
    status === "indexing_inprogress" ||
    status === "retrieval_inprogress" ||
    status === "eval_inprogress" ||
    status === "in_progress"
  ) {
    return "i-lucide-loader";
  } else if (
    status === "indexing_completed" ||
    status === "retrieval_completed"
  ) {
    return "i-lucide-check";
  } else if (status === "failed") {
    return "i-lucide-x";
  } else {
    return "i-lucide-circle-alert";
  }
};

export const useExperimentStatusColor = (status: ProjectExperimentStatus) => {
  if (status === "not_started") {
    return "neutral";
  } else if (status === "failed") {
    return "error";
  } else if (status === "succeeded") {
    return "success";
  } else if (
    status === "indexing_inprogress" ||
    status === "retrieval_inprogress" ||
    status === "eval_inprogress"
  ) {
    return "info";
  } else if (
    status === "indexing_completed" ||
    status === "retrieval_completed"
  ) {
    return "info";
  } else {
    return "neutral";
  }
};

export const useInfraAlertState = createGlobalState(() => {
  const isInfraAlertHidden = ref(false);
  return { isInfraAlertHidden };
});

export const useHumanChunkingStrategy = (strategy: string) => {
  switch (strategy) {
    case "fixed":
      return "Fixed";
    case "Fixed":
      return "Fixed";
    case "hierarchical":
      return "Hierarchical";
  }
};

export const useHumanIndexingAlgorithm = (algorithm: string) => {
  switch (algorithm) {
    case "hnsw":
      return "HNSW";
    case "hnsw_pq":
      return "HNSW - PQ";
    case "hnsw_sq":
      return "HNSW - SQ";
    case "hnsw_bq":
      return "HNSW - BQ";
  }
};

export const useHumanCurrencyAmount = (amount: number) => {
  return Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
};

export const useHumanModelService = (id: string) => {
  if (id === "bedrock") {
    return "Bedrock";
  } else if (id === "sagemaker") {
    return "SageMaker";
  }
};

export const useHumanDuration = (durationInMins: number) => {
  // if less than 60 minutes, return minutes
  if (durationInMins < 60) {
    return `${durationInMins}m`;
  }
  // if more than 60 minutes, return hours and minutes
  return `${Math.floor(durationInMins / 60)}h ${durationInMins % 60}m`;
};
