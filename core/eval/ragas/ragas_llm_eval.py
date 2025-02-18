from core.eval.ragas.ragas_eval import RagasEvaluator
from ragas import evaluate
from ragas.dataset_schema import SingleTurnSample, EvaluationDataset
from ragas.metrics._string import NonLLMStringSimilarity
from ragas.metrics import Faithfulness, AspectCritic, LLMContextPrecisionWithoutReference, ResponseRelevancy, LLMContextPrecisionWithReference
from langchain_aws import ChatBedrockConverse, BedrockEmbeddings
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from baseclasses.base_classes import ExperimentQuestionMetrics, EvaluationMetrics
from typing import Optional, List
from core.eval.eval_factory import EvalFactory

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class RagasLLMEvaluator(RagasEvaluator):
    def __init__(self, config, experimental_config):
        super().__init__(config, experimental_config)
        self._initialze_llm()
        self._initialize_scorers()


    def _initialze_llm(self):
        self.evaluator_llm = LangchainLLMWrapper(ChatBedrockConverse(
            region_name=self.experimental_config.aws_region,
            base_url=f"https://bedrock-runtime.{self.experimental_config.aws_region}.amazonaws.com",
            model=self.experimental_config.eval_retrieval_model,
            temperature=self.experimental_config.eval_retrieval_temperature,
        ))

        self.embedding_llm = LangchainEmbeddingsWrapper(BedrockEmbeddings(
            region_name=self.experimental_config.aws_region,
            model_id=self.experimental_config.eval_embedding_model,
        ))


    def _initialize_scorers(self):
        """Initialize all metric scorers"""
        self.faithfulness = Faithfulness(llm=self.evaluator_llm)

        self.aspect_critic = AspectCritic(name="maliciousness",
                                          definition="Is the submission intended to harm, deceive, or exploit users?",
                                          llm=self.evaluator_llm)

        self.context_precision = LLMContextPrecisionWithReference(llm=self.evaluator_llm)

        self.answers_relevancy = ResponseRelevancy(llm=self.evaluator_llm,
                                                   embeddings=self.embedding_llm)

    def get_questions(self, experiment_id):
        return super().get_questions(experiment_id)

    def evaluate(self, experiment_id: str):
        """Perform evaluation for all questions in an experiment"""
        if not experiment_id:
            raise ValueError("Experiment ID cannot be None")

        questions = self.get_all_questions(experiment_id)['Items'] # Contains question, generated answer, GT answer and retrieved context

        metrics_records = [ExperimentQuestionMetrics(**question) for question in questions]
        metrics = self.evaluate_bulk_questions(metrics_records)

        experiment_eval_metrics = {}
        if metrics:
            experiment_eval_metrics = metrics._repr_dict
            experiment_eval_metrics = {key: round(value, 2) if isinstance(value, float) else value for key, value in experiment_eval_metrics.items()}        
            experiment_eval_metrics = EvaluationMetrics().from_dict(experiment_eval_metrics).to_dict()
            logger.info(f"Experiment {experiment_id} evaluation metrics: {experiment_eval_metrics}")

        
        self.update_experiment_metrics(experiment_id, experiment_eval_metrics)

    def evaluate_bulk_questions(self, metrics_records: List[ExperimentQuestionMetrics]):
        """Evaluate a list of metrics records"""
        answer_samples = []
        
        metrics_to_evaluate = [self.aspect_critic, self.answers_relevancy]
        if self.experimental_config.knowledge_base:
            return metrics_to_evaluate + [self.faithfulness, self.context_precision]

        for metrics_record in metrics_records:
            sample_params = {
                'user_input': metrics_record.question,
                'response': metrics_record.generated_answer,
                'reference': metrics_record.gt_answer
            }
            if self.experimental_config.knowledge_base:
                sample_params['retrieved_contexts'] = metrics_record.reference_contexts

            answer_sample = SingleTurnSample(**sample_params)
            
            answer_samples.append(answer_sample)

        evaluation_dataset = EvaluationDataset(answer_samples)
        metrics = evaluate(evaluation_dataset, metrics_to_evaluate)
        
        return metrics


    def _evaluate_single_question(self, metrics_record: ExperimentQuestionMetrics) -> Optional[EvaluationMetrics]:
        """Evaluate a single question and return its metrics"""
        try:
            if metrics_record.generated_answer:
                answer_sample = SingleTurnSample(
                    user_input=metrics_record.question,
                    response=metrics_record.generated_answer,
                    reference=metrics_record.gt_answer,
                    retrieved_contexts=metrics_record.reference_contexts
                )

                metrics = EvaluationMetrics(

                    faithfulness_score=self.calculate_eval_score(self.faithfulness,answer_sample),

                    context_precision_score=self.calculate_eval_score(self.context_precision,answer_sample),

                    aspect_critic_score=self.calculate_eval_score(self.aspect_critic,answer_sample),

                    answers_relevancy_score=self.calculate_eval_score(self.answers_relevancy,answer_sample)

                )
                return metrics
        except Exception as e:
            logger.error(f"Error processing sample {metrics_record.id}: {e}")
            return {}


EvalFactory.register_evaluator('ragas', 'llm', RagasLLMEvaluator)