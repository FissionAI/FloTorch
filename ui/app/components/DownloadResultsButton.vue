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
    if (props.questionMetrics) {
      const assessments = {
        "guardrail user query assessment":
          JSON.stringify(item.guardrail_input_assessment) || "-",
        "guardrail context assessment":
          JSON.stringify(item.guardrail_context_assessment) || "-",
        "guardrail model response assessment":
          JSON.stringify(item.guardrail_output_assessment) || "-",
      };
      delete item["guardrail_input_assessment"];
      delete item["guardrail_context_assessment"];
      delete item["guardrail_output_assessment"];
      return {
        ...item,
        ...assessments,
      };
    } else {
      return item;
    }
  });
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
  />
</template>
