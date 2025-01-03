import logging
from typing import Optional

from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import NonLLMStringSimilarity, NonLLMContextRecall, NonLLMContextPrecisionWithReference, RougeScore, \
    BleuScore

from baseclasses.base_classes import ExperimentQuestionMetrics, EvaluationMetrics
from core.eval.eval_factory import EvalFactory
from core.eval.ragas.ragas_eval import RagasEvaluator

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class RagasNonLLMEvaluator(RagasEvaluator):

    def __init__(self, config, experimental_config):
        super().__init__(config, experimental_config)
        self._initialize_scorers()


    def _initialize_scorers(self):
        """Initialize all metric scorers"""
        self.str_similar_scorer = NonLLMStringSimilarity()
        self.context_recall = NonLLMContextRecall()
        self.context_precision = NonLLMContextPrecisionWithReference()
        self.rouge_score = RougeScore()
        self.bleu_score = BleuScore()

    def get_questions(self, experiment_id):
        return super().get_questions(experiment_id)

    def evaluate(self, experiment_id: str):
        """Perform evaluation for all questions in an experiment"""
        if not experiment_id:
            raise ValueError("Experiment ID cannot be None")

        questions = self.get_all_questions(experiment_id)['Items']
        metrics_list = []
        evaluation_dict = {}

        for question in questions:
            metrics_record = ExperimentQuestionMetrics(**question)
            metrics = self._evaluate_single_question(metrics_record)

            if metrics:
                metrics_list.append(metrics)
                update_expression = "SET eval_metrics = :metrics"
                expression_attribute_values = {
                    ':metrics': {'M' : metrics.to_dict()}
                }
                
                self.metrics_db.update_item(
                    key={'id': metrics_record.id},
                    update_expression=update_expression,
                    expression_values=expression_attribute_values
                )
        self.update_experiment_metrics(experiment_id, metrics_list)

    def _evaluate_single_question(self, metrics_record: ExperimentQuestionMetrics) -> Optional[EvaluationMetrics]:
        """Evaluate a single question and return its metrics"""
        try:
            answer_sample = SingleTurnSample(
                response=metrics_record.generated_answer,
                reference=metrics_record.gt_answer
            )

            context_sample = SingleTurnSample(
                retrieved_contexts=[metrics_record.generated_answer],
                reference_contexts=metrics_record.reference_contexts
            )

            metrics = EvaluationMetrics(
                string_similarity=self.calculate_eval_score(self.str_similar_scorer, answer_sample),
                context_precision=self.calculate_eval_score(self.context_precision, context_sample),
                context_recall=self.calculate_eval_score(self.context_recall, context_sample),
                rouge_score=self.calculate_eval_score(self.rouge_score,answer_sample)
            )

            return metrics
        except Exception as e:
            logger.error(f"Error processing sample {metrics_record.id}: {e}")
            return None

EvalFactory.register_evaluator('ragas', 'non_llm', RagasNonLLMEvaluator)