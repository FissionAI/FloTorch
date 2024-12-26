from core.opensearch_vectorstore import OpenSearchVectorDatabase
from config.experimental_config import ExperimentalConfig
from util.s3util import S3Util
from baseclasses.base_classes import ExperimentQuestionMetrics
from core.dynamodb import DynamoDBOperations
from config.config import Config, get_config
from core.processors import EmbedProcessor
from core.processors import InferenceProcessor
from core.rerank.rerank import DocumentReranker
import time

import boto3
from core.inference.inference_factory import InferencerFactory
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Function to retrieve and process data using Vectorstore and inference models
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import asdict

def retrieve(config: Config, experimentalConfig: ExperimentalConfig) -> None:
    """
    Execute the retrieval process for question answering experiments.
    
    Args:
        config (Config): Global configuration object
        experimentalConfig (ExperimentalConfig): Experiment-specific configuration
        
    Raises:
        RetrievalError: If the retrieval process fails
    """
    try:
        logger.info(f"Starting retrieval process for experiment ID: {experimentalConfig.experiment_id}")
        
        # Initialize all required components
        components = initialize_components(config, experimentalConfig)
        
        # Process ground truth data
        gt_data = load_ground_truth_data(experimentalConfig)
        
        # Process questions and store results
        (
            retrieval_query_embed_tokens,
            retrieval_input_tokens,
            retrieval_output_tokens,
        ) = process_questions(
            gt_data=gt_data,
            components=components,
            config=config,
            experimentalConfig=experimentalConfig,
        )


        components['experiment_dynamodb'].update_item(
            key={"id": experimentalConfig.experiment_id},
            update_expression="SET retrieval_query_embed_tokens = :rqembed, retrieval_input_tokens = :rinput, retrieval_output_tokens = :routput",
            expression_values={
                ":rqembed": retrieval_query_embed_tokens,
                ":rinput": retrieval_input_tokens,
                ":routput": retrieval_output_tokens,
            },
        )
        
        logger.info("Retrieval process completed successfully")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise RetrievalError(f"Retrieval process failed: {str(e)}")

def initialize_components(config: Config, experimentalConfig: ExperimentalConfig) -> Dict[str, Any]:
    """Initialize all required components for the retrieval process."""
    try:
        # Initialize embedding processor
        logger.info("Initializing embedding processor")
        embed_processor = EmbedProcessor(experimentalConfig)
        
        # Initialize inference processor
        logger.info("Initializing inference processor")
        inference_processor = InferenceProcessor(experimentalConfig)
        
        # Initialize vector database
        logger.info(f"Connecting to OpenSearch at {config.opensearch_host}")
        vector_database = OpenSearchVectorDatabase(
            host=config.opensearch_host,
            is_serverless=config.opensearch_serverless,
            region=config.aws_region,
            username=config.opensearch_username,
            password=config.opensearch_password
        )
        
        # Initialize DynamoDB connections
        logger.info("Initializing DynamoDB connections")
        metrics_dynamodb = DynamoDBOperations(
            region=config.aws_region,
            table_name=config.experiment_question_metrics_table
        )

        experiment_dynamodb = DynamoDBOperations(
            region=config.aws_region, table_name=config.experiment_table
        )

        return {
            "embed_processor": embed_processor,
            "inference_processor": inference_processor,
            "vector_database": vector_database,
            "metrics_dynamodb": metrics_dynamodb,
            "experiment_dynamodb": experiment_dynamodb
        }
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {str(e)}")
        raise

def load_ground_truth_data(experimentalConfig: ExperimentalConfig) -> List[Dict]:
    """Load ground truth data from S3."""
    logger.info(f"Reading ground truth data from S3: {experimentalConfig.gt_data}")
    return S3Util().read_json_from_s3(experimentalConfig.gt_data)

def process_questions(
    gt_data: List[Dict],
    components: Dict[str, Any],
    config: Config,
    experimentalConfig: ExperimentalConfig,
) -> Tuple[int, int, int]:
    """Process questions and store results in DynamoDB."""
    batch_items = []
    logger.info(f"Processing {len(gt_data)} questions from ground truth data")

    retrieval_query_embed_tokens = 0
    retrieval_input_tokens = 0
    retrieval_output_tokens = 0

    logger.info(f"Rerank model id for experiment {experimentalConfig.experiment_id}: {experimentalConfig.rerank_model_id}")
    for idx, item in enumerate(gt_data):
        try:
            question = item["question"]
            logger.debug(f"Processing question {idx+1}: {question}")

            # Generate embeddings
            query_metadata, query_embedding = components["embed_processor"].embed_text(
                question
            )
            retrieval_query_embed_tokens += int(query_metadata["inputTokens"])

            # Search for relevant context
            query_results = components["vector_database"].search(
                experimentalConfig.index_id, query_embedding, experimentalConfig.knn_num
            )

            if experimentalConfig.rerank_model_id and experimentalConfig.rerank_model_id.lower() != 'none':
                #Rerank the query results
                logger.info(f"Into reranking for experiment {experimentalConfig.experiment_id} for question {idx+1}")
                start_time = time.time()
                reranker = DocumentReranker(region=experimentalConfig.aws_region, rerank_model_id=experimentalConfig.rerank_model_id)  
                query_results = reranker.rerank_documents(question, query_results)
                end_time = time.time()
                logger.info(f"Reranking for question {idx+1} took {end_time - start_time:.2f} seconds")                
            

            # Generate answer
            answer_metadata, answer = components["inference_processor"].generate_text(
                user_query=question,
                context=query_results,
                default_prompt=config.inference_system_prompt,
            )
            retrieval_input_tokens += int(answer_metadata["inputTokens"])
            retrieval_output_tokens += int(answer_metadata["outputTokens"])

            reference_contexts = (
                [record["text"] for record in query_results] if query_results else []
            )

            #  Update the metrics here to store the DynamoDb Table
            metrics = _create_metrics(
                experimental_config=experimentalConfig,
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
                write_batch_to_dynamodb(batch_items, components["metrics_dynamodb"])
                batch_items = []
        except Exception as e:
            logger.error(f"Error processing question {idx+1}: {str(e)}")
            metrics = metrics = _create_metrics(
                experimental_config=experimentalConfig,
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
        write_batch_to_dynamodb(batch_items, components["metrics_dynamodb"])
    logger.info(f"Experiment {experimentalConfig.experiment_id} Retrieval Tokens : \n Query Embed Tokens : {retrieval_query_embed_tokens} \n Input Tokens : {retrieval_input_tokens} \n Output Tokens : {retrieval_output_tokens}")
    return (retrieval_query_embed_tokens, retrieval_input_tokens, retrieval_output_tokens)


def _create_metrics(
    experimental_config: ExperimentalConfig,
    question: str,
    answer: str,
    gt_answer: str,
    reference_contexts: List[str],
    query_metadata: Dict[str, int],
    answer_metadata: Dict[str, int],
) -> "ExperimentQuestionMetrics":
    """Create metrics object with provided data."""
    return ExperimentQuestionMetrics(
        execution_id=experimental_config.execution_id,
        experiment_id=experimental_config.experiment_id,
        question=question,
        gt_answer=gt_answer,
        generated_answer=answer,
        reference_contexts=reference_contexts,
        query_metadata=query_metadata,
        answer_metadata=answer_metadata,
    )

def write_batch_to_dynamodb(batch_items: List[Dict], dynamodb: DynamoDBOperations) -> None:
    """Write a batch of items to DynamoDB."""
    logger.info(f"Writing batch of {len(batch_items)} items to DynamoDB")
    dynamodb.batch_write(batch_items)
    
class RetrievalError(Exception):
    """Custom exception for retrieval process errors."""
    pass
