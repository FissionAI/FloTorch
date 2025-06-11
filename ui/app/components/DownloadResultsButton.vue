<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    results?: Record<string, any>[];
    buttonLabel: string;
    questionMetrics?: boolean;
  }>(),
  {
    results: () => [],
    buttonLabel: "Download Results",
    questionMetrics : false
  }
);

const downloadResults = () => {
  const stringifyData = props.results.map((item) => {
    const eval_metrics = item.eval_metrics?.M
    const total_time = item.total_time * 60
    if (props.questionMetrics) {
      const assessments = {
        "Guardrail User Query":
          JSON.stringify(item.guardrail_input_assessment) || "-",
        "Guardrail Context":
          JSON.stringify(item.guardrail_context_assessment) || "-",
        "Guardrail Model Response":
          JSON.stringify(item.guardrail_output_assessment) || "-",
      };
      delete item["guardrail_input_assessment"];
      delete item["guardrail_context_assessment"];
      delete item["guardrail_output_assessment"];
      const { id, ...rest } = item;
      return {
        ...{"Question": item.question, "Ground Truth": item.gt_answer, "Generated Answer": item.generated_answer},
        ...assessments,
      };
    } else {
      const results = {
        "ID": item.id,
        "Status": item.experiment_status,
        "Inferencing Model": item.config.retrieval_model,
        "Estimated Cost": item.cost || (item.cost === 0 ? 0 : "NA"),
        "Faithfulness": item.eval_metrics?.M?.faithfulness_score ||item.eval_metrics?.faithfulness_score || (item.eval_metrics?.M?.faithfulness_score === 0 ? 0 : "NA"),
        "Context Precision":
        item.eval_metrics?.M?.context_precision_score || item.eval_metrics?.context_precision_score || (item.eval_metrics?.M?.context_precision_score === 0 ? 0 : "NA"),
        "Maliciousness":
          item.eval_metrics?.M?.aspect_critic_score ||item.eval_metrics?.aspect_critic_score || (item.eval_metrics?.M?.aspect_critic_score === 0 ? 0 : "NA"),
        "Answer Relevancy":
          item.eval_metrics?.M?.answers_relevancy_score ||item.eval_metrics?.answers_relevancy_score || (item.eval_metrics?.M?.answers_relevancy_score === 0 ? 0 : "NA"),
        "Duration": item.total_time || (item.total_time === 0 ? 0 : "NA"),
        "Embedding Model": item.config.embedding_model || "NA",
        "Evaluation Service": item.config.eval_service,
        "Evaluation Embedding Model":
          item.config.eval_embedding_model,
        "Evaluation Inferencing Model":
          item.config.eval_retrieval_model,
        "Directional Cost": item.config.directional_pricing || (item.config.directional_pricing === 0 ? 0 : "NA"),
        "Indexing Algorithm": item.config.indexing_algorithm || "NA",
        "Chunking": item.config.chunking_strategy || "NA",
        "Inferencing Model Temperature": item.config.temp_retrieval_llm || (item.config.temp_retrieval_llm === 0 ? 0 : "NA"),
        "Reranking Model": item.config.rerank_model_id || "NA",
        "Guardrail": item.config?.guardrail_name || "NA",
        "Bedrock KB Name": item.config?.kb_name || "NA",
        // "KNN": item.config?.knn_num === 'nan' ? "NA" : item.config?.knn_num || (item.config?.knn_num === 0 ? 0 : "NA"),
        "KNN": item.config.knn_num ? item.config.knn_num : "NA",
        "N Shot Prompts": item.config.n_shot_prompts || (item.config.n_shot_prompts === 0 ? 0 : "NA"),
        "Expert Evaluation Scores": item.scores || (item.scores === 0 ? 0 : "NA"),
      }

      return results;
    }
  });
  if (!props.questionMetrics) {
    stringifyData.sort((a, b) => a.ID.localeCompare(b.ID));
  }
  const csv = jsonToCsv(stringifyData);
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "results.csv";
  a.click();
};
</script>

<template>
  <UButton
    :label="buttonLabel"
    icon="i-lucide-download"
    @click="downloadResults"
    class="primary-btn"
  />
</template>