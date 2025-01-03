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
            retrieval_query_embed_tokens, retrieval_input_tokens, retrieval_output_tokens = self.process_questions(
                gt_data, components)

            # Log DynamoDB update
            self.log_dynamodb_update(retrieval_query_embed_tokens, retrieval_input_tokens, retrieval_output_tokens)

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

        logger.info(
            f"Rerank model id for experiment {self.experimentalConfig.experiment_id}: {self.experimentalConfig.rerank_model_id}")
        for idx, item in enumerate(gt_data):
            try:
                question = item["question"]
                logger.debug(f"Processing question {idx + 1}: {question}")

                # Generate embeddings
                query_metadata, query_embedding = components["embed_processor"].embed_text(
                    question
                )
                retrieval_query_embed_tokens += int(query_metadata["inputTokens"])

                # Search for relevant context
                query_results = components["vector_database"].search(
                    self.experimentalConfig.index_id, query_embedding, self.experimentalConfig.knn_num
                )

                if self.experimentalConfig.chunking_strategy.lower() == 'hierarchical':
                    overall_documents = []
                    parent_dict = {}
                    for document in query_results:
                        temp_document = document
                        parent_id = document.get('parent_id')
                        if parent_id not in parent_dict:
                            overall_documents.append(temp_document)
                            parent_dict[parent_id] = 1
                    query_results = overall_documents

                if self.experimentalConfig.rerank_model_id and self.experimentalConfig.rerank_model_id.lower() != 'none':
                    # Rerank the query results
                    logger.info(
                        f"Into reranking for experiment {self.experimentalConfig.experiment_id} for question {idx + 1}")
                    start_time = time.time()
                    reranker = DocumentReranker(region=self.experimentalConfig.aws_region,
                                                rerank_model_id=self.experimentalConfig.rerank_model_id)
                    query_results = reranker.rerank_documents(question, query_results)
                    end_time = time.time()
                    logger.info(f"Reranking for question {idx + 1} took {end_time - start_time:.2f} seconds")

                # Generate answer
                answer_metadata, answer = components["inference_processor"].generate_text(
                    user_query=question,
                    context=query_results,
                    default_prompt=self.config.inference_system_prompt,
                )
                retrieval_input_tokens += int(answer_metadata["inputTokens"])
                retrieval_output_tokens += int(answer_metadata["outputTokens"])

                reference_contexts = (
                    [record["text"] for record in query_results] if query_results else []
                )

                #  Update the metrics here to store the DynamoDb Table
                metrics = self._create_metrics(
                    experimental_config=self.experimentalConfig,
                    question=question,
                    answer=answer,
                    gt_answer=item["answer"],
                    reference_contexts=reference_contexts,
                    query_metadata=query_metadata,
                    answer_metadata=answer_metadata,
                )

                batch_items.append(metrics.to_dynamo_item())

                # batch_items.append(metrics.__dict__)

                # Write batch if size reaches threshold
                if len(batch_items) >= 25:
                    self.write_batch_to_dynamodb(batch_items, components["metrics_dynamodb"])
                    batch_items = []
            except Exception as e:
                logger.error(f"Error processing question {idx+1}: {str(e)}")
                metrics = metrics = self._create_metrics(
                    experimental_config=self.experimentalConfig,
                    question=question,
                    answer="",
                    gt_answer=item["answer"],
                    reference_contexts=[],
                    query_metadata={},
                    answer_metadata={},
                )
                batch_items.append(metrics.to_dynamo_item())
                continue

        # Write remaining items
        if batch_items:
            self.write_batch_to_dynamodb(batch_items, components["metrics_dynamodb"])
        logger.info(f"Experiment {self.experimentalConfig.experiment_id} Retrieval Tokens : \n Query Embed Tokens : {retrieval_query_embed_tokens} \n Input Tokens : {retrieval_input_tokens} \n Output Tokens : {retrieval_output_tokens}")
        return (retrieval_query_embed_tokens, retrieval_input_tokens, retrieval_output_tokens)


class RetrievalError(Exception):
    """Custom exception for retrieval process errors."""
    pass
