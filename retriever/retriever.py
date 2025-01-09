import logging
import time
from typing import Tuple, List, Dict

from baseclasses.base_pipeline import BasePipeline
from core.rerank.rerank import DocumentReranker
from util.s3util import S3Util

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Retriever(BasePipeline):
    def execute(self) -> None:
        """Execute the retrieval process for question answering experiments."""
        try:
            logger.info(f"Starting retrieval process for experiment ID: {self.experimentalConfig.experiment_id}")

            # Initialize all required components
            components = self.initialize_components()

            # Process ground truth data
            gt_data = self.load_ground_truth_data()

            # Process questions and store results
            retrieval_tokens = self.process_questions(gt_data, components)

            # Log DynamoDB update
            self.log_dynamodb_update(*retrieval_tokens)

            logger.info("Retrieval process completed successfully")

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            raise RetrievalError(f"Retrieval process failed: {str(e)}")

    def load_ground_truth_data(self) -> List[Dict]:
        """Load ground truth data from S3."""
        logger.info(f"Reading ground truth data from S3: {self.experimentalConfig.gt_data}")
        return S3Util().read_text_from_s3(self.experimentalConfig.gt_data)

    def process_questions(self, gt_data, components) -> Tuple[int, int, int]:
        """Process questions from ground truth data."""
        batch_items = []
        retrieval_query_embed_tokens = 0
        retrieval_input_tokens = 0
        retrieval_output_tokens = 0

        for idx, item in enumerate(gt_data):
            try:
                question = item["question"]
                logger.debug(f"Processing question {idx + 1}: {question}")

                # Process the question and generate embeddings
                query_metadata, query_embedding = self.process_question_embedding(question, components)
                retrieval_query_embed_tokens += int(query_metadata["inputTokens"])

                # Retrieve relevant context based on the query
                query_results = self.retrieve_relevant_context(query_embedding, components)

                # Optionally, rerank the results
                query_results = self.rerank_results(question, query_results, idx)

                # Generate answer from context
                answer_metadata, answer = self.generate_answer(question, query_results, components)
                retrieval_input_tokens += int(answer_metadata["inputTokens"])
                retrieval_output_tokens += int(answer_metadata["outputTokens"])

                # Collect the reference contexts for metrics
                reference_contexts = self.get_reference_contexts(query_results)

                # Create and store metrics
                metrics = self.create_metrics(item, question, answer, reference_contexts, query_metadata, answer_metadata)
                batch_items.append(metrics.to_dynamo_item())

                # Write batch if size reaches threshold
                if len(batch_items) >= 25:
                    self.write_batch_to_dynamodb(batch_items, components["metrics_dynamodb"])
                    batch_items = []

            except Exception as e:
                logger.error(f"Error processing question {idx + 1}: {str(e)}")
                metrics = self.create_error_metrics(item, question)
                batch_items.append(metrics.to_dynamo_item())
                continue

        # Write remaining items
        if batch_items:
            self.write_batch_to_dynamodb(batch_items, components["metrics_dynamodb"])

        logger.info(f"Experiment {self.experimentalConfig.experiment_id} Retrieval Tokens : "
                    f"\n Query Embed Tokens : {retrieval_query_embed_tokens} \n Input Tokens : {retrieval_input_tokens} \n Output Tokens : {retrieval_output_tokens}")

        return retrieval_query_embed_tokens, retrieval_input_tokens, retrieval_output_tokens

    def process_question_embedding(self, question: str, components) -> Tuple[Dict, List[float]]:
        """Generate embeddings for the question."""
        logger.debug(f"Generating embedding for question: {question}")
        return components["embed_processor"].embed_text(question)

    def retrieve_relevant_context(self, query_embedding: List[float], components) -> List[Dict]:
        """Retrieve the relevant context based on the query embedding."""
        logger.debug("Searching for relevant context based on query embedding")
        return components["vector_database"].search(
            self.experimentalConfig.index_id, query_embedding, self.experimentalConfig.knn_num
        )

    def rerank_results(self, question: str, query_results: List[Dict], idx: int) -> List[Dict]:
        """Rerank the query results if a rerank model is defined."""
        if self.experimentalConfig.rerank_model_id and self.experimentalConfig.rerank_model_id.lower() != 'none':
            logger.info(f"Reranking results for question {idx + 1}: {question}")
            reranker = DocumentReranker(
                region=self.experimentalConfig.aws_region,
                rerank_model_id=self.experimentalConfig.rerank_model_id
            )
            start_time = time.time()
            query_results = reranker.rerank_documents(question, query_results)
            end_time = time.time()
            logger.info(f"Reranking took {end_time - start_time:.2f} seconds")
        return query_results

    def generate_answer(self, question: str, query_results: List[Dict], components) -> Tuple[Dict, str]:
        """Generate the answer based on the question and context."""
        logger.debug(f"Generating answer for question: {question}")
        return components["inference_processor"].generate_text(
            user_query=question,
            context=query_results,
            default_prompt=self.config.inference_system_prompt,
        )

    def get_reference_contexts(self, query_results: List[Dict]) -> List[str]:
        """Extract reference contexts from query results."""
        return [record["text"] for record in query_results] if query_results else []

    def create_metrics(self, item, question, answer, reference_contexts, query_metadata, answer_metadata):
        """Create and return metrics to store."""
        return self._create_metrics(
            experimental_config=self.experimentalConfig,
            question=question,
            answer=answer,
            gt_answer=item["answer"],
            reference_contexts=reference_contexts,
            query_metadata=query_metadata,
            answer_metadata=answer_metadata,
        )

    def create_error_metrics(self, item, question):
        """Create error metrics for failed processing."""
        return self._create_metrics(
            experimental_config=self.experimentalConfig,
            question=question,
            answer="",
            gt_answer=item["answer"],
            reference_contexts=[],
            query_metadata={},
            answer_metadata={},
        )


class RetrievalError(Exception):
    """Custom exception for retrieval process errors."""
    pass