import { z } from "zod";

export const ProjectsListQuerySchema = z.object({
  page: z.coerce.number().default(1),
  limit: z.coerce.number().default(20),
  search: z.string().optional(),
});

export type ProjectsListQuery = z.infer<typeof ProjectsListQuerySchema>;

export const ProjectCreateModelSchema = z.object({
  service: z.string(),
  value: z.string(),
  label: z.string(),
});

export const ProjectCreateDataStrategySchema = z.object({
  name: z.string({
    required_error: "Name is required",
  }),
  region: z.string({
    required_error: "Region is required",
  }),
  kb_data: z.string({
    required_error: "Knowledge Base data is required",
  }),
  gt_data: z.string({
    required_error: "Ground Truth data is required",
  }),
});

export type ProjectCreateDataStrategy = z.infer<
  typeof ProjectCreateDataStrategySchema
>;

export const ProjectCreateIndexingStrategySchema = z.object({
  chunking_strategy: z
    .string({
      required_error: "At least one chunking is required",
    })
    .array()
    .min(1, {
      message: "At least one indexing strategy is required",
    }),
  chunk_size: z
    .number({
      required_error: "At least one chunk size is required",
    })
    .array()
    .min(1, {
      message: "At least one chunk size is required",
    }),
  chunk_overlap: z
    .number({
      required_error: "At least one chunk overlap percentage is required",
    })
    .array()
    .min(1, {
      message: "At least one chunk overlap percentage is required",
    }),
  vector_dimension: z
    .number({
      required_error: "At least one vector dimension is required",
    })
    .array()
    .min(1, {
      message: "At least one vector dimension is required",
    }),
  indexing_algorithm: z
    .string({
      required_error: "At least one indexing algorithm is required",
    })
    .array()
    .min(1, {
      message: "At least one indexing algorithm is required",
    }),
  embedding: ProjectCreateModelSchema.array().min(1, {
    message: "At least one embedding model is required",
  }),
});

export type ProjectCreateIndexingStrategy = z.infer<
  typeof ProjectCreateIndexingStrategySchema
>;

export const ProjectNShotPromptGuideSchema = z.object({
  user_prompt: z.string({
    required_error: "User prompt is required",
  }),
  examples: z
    .array(
      z.object({
        example: z.string({
          required_error: "Example is required",
        }),
      })
    )
    .optional(),
  system_prompt: z.string({
    required_error: "System prompt is required",
  }),
});

export type ProjectNShotPromptGuide = z.infer<
  typeof ProjectNShotPromptGuideSchema
>;

export const ProjectCreateRetrievalStrategySchema = z
  .object({
    rerank_model_id: z.string({
      required_error: "At least one rerank model is required",
    }).array().min(1, {
      message: "At least one rerank model is required",
    }),
    n_shot_prompts: z
      .number({
        required_error: "At least one shot prompt is required",
      })
      .array()
      .min(1, {
        message: "At least one shot prompt is required",
      }),
    knn_num: z
      .number({
        required_error: "At least one KNN is required",
      })
      .array()
      .min(1, {
        message: "At least one KNN is required",
      }),
    temp_retrieval_llm: z
      .number({
        required_error: "At least one retrieval LLM temperature is required",
      })
      .array()
      .min(1, {
        message: "At least one retrieval LLM temperature is required",
      }),
    retrieval: ProjectCreateModelSchema.array().min(1, {
      message: "At least one retrieval model is required",
    }),
    n_shot_prompt_guide: ProjectNShotPromptGuideSchema,
  })
  .superRefine((data, ctx) => {
    if (
      data.n_shot_prompts &&
      useMax(data.n_shot_prompts || [0]).value > 0 &&
      !data.n_shot_prompt_guide
    ) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Required when N Shot Prompts is greater than 0",
        path: ["n_shot_prompt_guide"],
      });
    }
  });

export type ProjectCreateRetrievalStrategy = z.infer<
  typeof ProjectCreateRetrievalStrategySchema
>;

export const ProjectExperimentStatusSchema = z.enum([
  "not_started",
  "in_progress",
  "indexing_inprogress",
  "indexing_completed",
  "retrieval_inprogress",
  "retrieval_completed",
  "eval_inprogress",
  "eval_completed",
  "failed",
  "succeeded",
]);

export type ProjectExperimentStatus = z.infer<
  typeof ProjectExperimentStatusSchema
>;

export const ProjectStatusSchema = z.enum([
  "not_started",
  "in_progress",
  "completed",
  "failed",
]);

export type ProjectStatus = z.infer<typeof ProjectStatusSchema>;
export interface ProjectListItem {
  id: string;
  date: Date;
  status: ProjectStatus;
  gt_data: string;
  kb_data: string;
  region: string;
  name: string;
}

export interface Project {
  id: string;
  name: string;
  date: Date;
  status: ProjectStatus;
  gt_data: string;
  kb_data: string;
  region: string;
  config: Config;
}

export interface Config {
  prestep: Prestep;
  indexing: Indexing;
  n_shot_prompt_guide: NShotPromptGuide;
  retrieval: Retrieval;
}

export interface Indexing {
  chunking_strategy: string[];
  vector_dimension: number[];
  chunk_size: number[];
  embedding: Embedding[];
  chunk_overlap: number[];
  indexing_algorithm: string[];
}

export interface Embedding {
  model: string;
  service: string;
}

export interface NShotPromptGuide {
  user_prompt: string;
  examples: Example[];
  system_prompt: string;
}

export interface Example {
  prompt: string;
}

export interface Prestep {
  region: string;
  gt_data: string;
  kb_data: string;
}

export interface Retrieval {
  knn_num: number[];
  temp_retrieval_llm: number[];
  n_shot_prompts: number[];
  retrieval: Embedding[];
}

export interface ProjectExperimentConfig {
  temp_retrieval_llm: number;
  vector_dimension: number;
  gt_data: string;
  chunk_size: number;
  n_shot_prompts: number;
  embedding_service: string;
  embedding_model: string;
  kb_data: string;
  retrieval_service: string;
  chunking_strategy: string;
  knn_num: number;
  retrieval_model: string;
  id: number;
  region: string;
  chunk_overlap: number;
  indexing_algorithm: string;
  directional_pricing: number;
}

export interface EvalMetrics {
  faithfulness_score: number;
  context_precision_score: number;
  aspect_critic_score: number;
  answers_relevancy_score: number;
}

export interface EvalMetricsM {
  M?: EvalMetrics;
}

export interface ProjectExperiment {
  last_updated: Date;
  start_datetime: Date;
  experiment_status: ProjectExperimentStatus;
  config: ProjectExperimentConfig;
  timestamp: Date;
  indexing_time: number;
  index_id: string;
  total_time: number;
  cost: number;
  retrieval_time: number;
  execution_id: string;
  retrieval_status: string;
  id: string;
  end_datetime: null;
  index_status: string;
  experiment_duration: number;
  eval_metrics: EvalMetrics | EvalMetricsM;
}

export const ProjectCreateSchema = z.object({
  name: z.string({ required_error: "Name is required" }),
  prestep: ProjectCreateDataStrategySchema,
  indexing: ProjectCreateIndexingStrategySchema,
  retrieval: ProjectCreateRetrievalStrategySchema,
  n_shot_prompt_guide: ProjectNShotPromptGuideSchema,
});

export type ProjectCreate = z.infer<typeof ProjectCreateSchema>;
