export interface ValidExperiment {
  region: string;
  chunking_strategy: string;
  vector_dimension: number;
  chunk_size: number;
  chunk_overlap: number;
  indexing_algorithm: string;
  knn_num: number;
  temp_retrieval_llm: number;
  n_shot_prompts: number;
  embedding_service: string;
  embedding_model: string;
  retrieval_service: string;
  retrieval_model: string;
  directional_pricing: number;
  rerank_model_id: string;
}

export interface ExperimentQuestionMetric {
  question: string;
  execution_id: string;
  reference_contexts: string[];
  experiment_id: string;
  gt_answer: string;
  generated_answer: string;
  id: string;
  eval_metrics: EvalMetrics | EvalMetricsM;
}
