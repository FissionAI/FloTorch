import os
import boto3
from utils import read_csv_from_s3, parse_datetime
from datetime import datetime
import math
import logging

MILLION = 1_000_000
THOUSAND = 1_000
SECONDS_IN_MINUTE = 60
MINUTES_IN_HOUR = 60
HOURS_IN_DAY = 24
DAYS_IN_MONTH = 30

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

s3 = boto3.client("s3")
S3_BUCKET = os.getenv("s3_bucket")
BEDROCK_CSV_PATH = os.getenv("bedrock_limit_csv")


def compute_actual_price_breakdown(
    configuration, input_tokens, output_tokens, index_embed_tokens, query_embed_tokens, total_time, indexing_time, retrieval_time, eval_time, experiment_question_metrics_items
):
    """Compute the actual price based on the given configuration and token/time inputs."""

    is_input_valid, input_missing = validate_params(
        configuration=configuration
    )

    if not is_input_valid:
        logger.error(f"Missing required parameters: {', '.join(input_missing)}.")
        return None

    try:
        # Read pricing data from S3
        df = read_csv_from_s3(BEDROCK_CSV_PATH, S3_BUCKET)
    except Exception as e:
        logger.error(f"Error reading the CSV file from S3: {e}")
        return None

    try:
        aws_region = configuration.get("config", {}).get("region", "")
        embedding_model = configuration.get("config", {}).get("embedding_model", "")
        retrieval_model = configuration.get("config", {}).get("retrieval_model", "")
        embedding_service = configuration.get("config", {}).get("embedding_service", "")
        retrieval_service = configuration.get("config", {}).get("retrieval_service", "")
        bedrock_knowledge_base = configuration.get("config", {}).get("bedrock_knowledge_base", False)
        rerank_model_id = configuration.get("config", {}).get("rerank_model_id", None)
        is_opensearch = configuration.get("config", {}).get("is_opensearch", True)

        is_config_valid, config_missing = validate_params(
            aws_region=aws_region,
            retrieval_model=retrieval_model,
            retrieval_service=retrieval_service
        )
        if not is_config_valid:
            logger.error(
                f"Configuration is missing required fields: {', '.join(config_missing)}."
            )
            return None

        indexing_cost = 0
        retrieval_cost = 0
        inferencing_cost = 0
        eval_cost = 0
        total_cost = 0

        overall_metadata = {}
        indexing_metadata = {}
        retriever_metadata = {}
        inferencer_metadata = {}
        evaluator_metadata = {}

        query_embedding_cost = 0
        embedding_model_price = 0

        # Calculating indexing, inferencing and evaluation costs for bedrock/Sagemaker
        if not bedrock_knowledge_base:
            indexing_metadata['runtime'] = indexing_time
            indexing_metadata['model'] = embedding_model
            indexing_metadata['service'] = embedding_service
            if embedding_service == "bedrock" :
                embedding_model_price = df[(df["model"] == embedding_model) & (df["Region"] == aws_region)]["input_price"]
                if embedding_model_price.empty:
                    logger.error(f"No embedding model {embedding_model} price found.")
                    return None
                embedding_model_price = float(embedding_model_price.values[0])  # Price per 1000 tokens
                indexing_cost = (embedding_model_price * float(index_embed_tokens)) / THOUSAND
                indexing_metadata['knowledge_base_tokens'] = index_embed_tokens
                indexing_metadata['bedrock_cost'] = indexing_cost
            else:
                indexing_cost = sagemaker_cost(indexing_time)
                indexing_metadata['sagemaker_cost'] = indexing_cost
        
        retriever_metadata['runtime'] = retrieval_time

        inferencer_metadata['model'] = retrieval_model
        inferencer_metadata['service'] = retrieval_service
        if retrieval_service == "bedrock" :
            inferencer_metadata['input_tokens'] = input_tokens
            inferencer_metadata['output_tokens'] = output_tokens
            question_details = calculate_experiment_question_details(experiment_question_metrics_items)
            retriever_metadata['no_of_questions'] = question_details["total_questions"]

            inferencer_metadata['no_of_questions'] = question_details["total_questions"]
            inferencer_metadata['inference_time'] = question_details["overall_inferencer_time"]
            inferencer_metadata['average_latency'] = question_details["average_inferencer_time"]

            reranking_cost = 0

            retrieval_model_input_price = df[
                (df["model"] == retrieval_model) & (df["Region"] == aws_region)
            ]["input_price"]
            retrieval_model_output_price = df[
                (df["model"] == retrieval_model) & (df["Region"] == aws_region)
            ]["output_price"]

            if retrieval_model_input_price.empty:
                logger.error(f"No retrieval model {retrieval_model} input price found.")
                return None
            
            if retrieval_model_output_price.empty:
                logger.error(f"No retrieval model {retrieval_model} output price found.")
                return None
            
            retrieval_model_input_price = float(retrieval_model_input_price.values[0])  # Price per million tokens
            retrieval_model_output_price = float(retrieval_model_output_price.values[0])  # Price per million tokens
            # Calculate costs
            
            retrieval_model_input_actual_cost = (retrieval_model_input_price * float(input_tokens)) / MILLION
            retrieval_model_output_actual_cost = (retrieval_model_output_price * float(output_tokens)) / MILLION
            inferencer_metadata['input_tokens_cost'] = retrieval_model_input_actual_cost
            inferencer_metadata['output_tokens_cost'] = retrieval_model_output_actual_cost
            if (not bedrock_knowledge_base) and embedding_service == "bedrock":
                query_embedding_cost = (embedding_model_price * float(query_embed_tokens)) / THOUSAND
                inferencer_metadata['query_embed_tokens'] = query_embed_tokens
                inferencer_metadata['query_embed_tokens_cost'] = query_embedding_cost
            if rerank_model_id and rerank_model_id != "none" :
                retriever_metadata['rerank_model'] = rerank_model_id
                retriever_metadata['reranker_queries'] = question_details["reranker_queries"]
                reranker_model_price = df[(df["model"] == rerank_model_id) & (df["Region"] == aws_region)]["input_price"]
                if reranker_model_price.empty:
                    logger.error(f"No reranker model {rerank_model_id} price found.")
                    return None
                reranker_model_price = float(reranker_model_price.values[0])  # Price per 1000 queries
                reranking_cost = (reranker_model_price * float(question_details['reranker_queries'])) / THOUSAND
                retriever_metadata['reranking_cost'] = reranking_cost
                retrieval_cost += reranking_cost
            inferencing_cost = retrieval_model_input_actual_cost + retrieval_model_output_actual_cost + query_embedding_cost
        else:
            inferencer_metadata['runtime'] = retrieval_time
            inferencing_cost = sagemaker_cost(retrieval_time)
            inferencer_metadata['sagemaker_cost'] = inferencing_cost
            if not bedrock_knowledge_base:
                if embedding_service == "bedrock":
                    query_embedding_cost = (embedding_model_price * float(query_embed_tokens)) / THOUSAND
                    inferencing_cost += query_embedding_cost
                    inferencer_metadata['query_embed_tokens'] = query_embed_tokens
                    inferencer_metadata['query_embed_tokens_cost'] = query_embedding_cost
                else:
                    embedding_sagemaker_cost = sagemaker_cost(retrieval_time)
                    inferencing_cost += embedding_sagemaker_cost
                    inferencer_metadata['sagemaker_embedding_cost'] = embedding_sagemaker_cost

        inferencer_metadata['total_cost'] = inferencing_cost
        # Eval costs doesn't include ragas at the moment
        # Only adding sagemaker endpoint costs considering it is still running
        evaluator_metadata['runtime'] = eval_time
        if embedding_service == "sagemaker":
            eval_cost += sagemaker_cost(eval_time)
            evaluator_metadata['sagemaker_embedding_cost'] = eval_cost
        if retrieval_service == "sagemaker":
            eval_cost += sagemaker_cost(eval_time)
            evaluator_metadata['sagemaker_inferencer_cost'] = eval_cost
            
        #Calculating fargate container costs
        indexing_ecs_cost = ecs_cost(indexing_time)
        retriever_ecs_cost = ecs_cost(retrieval_time)
        eval_ecs_cost = ecs_cost(eval_time)

        if not bedrock_knowledge_base:
            indexing_cost += indexing_ecs_cost
            indexing_metadata['ecs_cost'] = indexing_ecs_cost

        retriever_metadata['ecs_cost'] = retriever_ecs_cost
        evaluator_metadata['ecs_cost'] = eval_ecs_cost

        retrieval_cost += retriever_ecs_cost
        eval_cost += eval_ecs_cost
        

        # Adding opensearch provisioned costs
        if not bedrock_knowledge_base and is_opensearch:
            indexing_os_cost = opensearch_cost(indexing_time)
            retriever_os_cost = opensearch_cost(retrieval_time)
            eval_os_cost = opensearch_cost(eval_time)

            indexing_metadata['opensearch_cost'] = indexing_os_cost
            retriever_metadata['opensearch_cost'] = retriever_os_cost
            evaluator_metadata['opensearch_cost'] = eval_os_cost

            indexing_cost += indexing_os_cost
            retrieval_cost += retriever_os_cost
            eval_cost += eval_os_cost

        indexing_metadata['total_cost'] = indexing_cost
        retriever_metadata['total_cost'] = retrieval_cost
        evaluator_metadata['total_cost'] = eval_cost
        
         
        total_cost = indexing_cost + retrieval_cost + inferencing_cost + eval_cost
        overall_metadata['total_cost'] = total_cost
        overall_metadata['total_time'] = total_time
        overall_metadata['order'] = ['total_time', 'total_cost']
        indexing_metadata['order'] = ['model', 'service', 'knowledge_base_tokens', 'bedrock_cost', 'runtime', 'sagemaker_cost', 'ecs_cost', 'opensearch_cost', 'total_cost']
        retriever_metadata['order'] = ['no_of_questions', 'rerank_model', 'reranker_queries', 'reranking_cost', 'runtime', 'ecs_cost', 'opensearch_cost', 'total_cost']
        inferencer_metadata['order'] = ['model', 'service', 'no_of_questions', 'input_tokens', 'output_tokens', 'query_embed_tokens', 'input_tokens_cost', 'output_tokens_cost', 'query_embed_tokens_cost', 'average_latency', 'runtime', 'sagemaker_embedding_cost', 'sagemaker_cost', 'total_cost']
        evaluator_metadata['order'] = ['runtime', 'ecs_cost', 'opensearch_cost', 'sagemaker_embedding_cost', 'sagemaker_inferencer_cost', 'total_cost']
        return overall_metadata, indexing_metadata, retriever_metadata, inferencer_metadata, evaluator_metadata
    
    except Exception as e:
        logger.error(f"Error during price computation: {e}")
        return None

def sagemaker_cost(time, number_of_instances = 1):
    instance_cost_per_hour = 1.210 #per hour ml.g5.2xlarge per model
    overall_cost = instance_cost_per_hour * number_of_instances * ((time / SECONDS_IN_MINUTE) / MINUTES_IN_HOUR)
    
    return overall_cost

def opensearch_cost(time):
    number_of_instances = 3

    instance_cost_per_hour = 0.711 # r7g.2xlarge.search
    instance_total_cost = (instance_cost_per_hour * number_of_instances * (time / SECONDS_IN_MINUTE) / MINUTES_IN_HOUR)

    ebs_volume_size = 10  # 2 GB
    ebs_volume_price_per_month = .122 
    ebs_total_cost = ebs_volume_price_per_month * ebs_volume_size * number_of_instances * ((time / SECONDS_IN_MINUTE) / MINUTES_IN_HOUR) / (HOURS_IN_DAY * DAYS_IN_MONTH) # 3 instances for 10GB each
    
    iops_cost_per_month = .008
    iops_per_instance = 16000  # instances per hour for 16000 IOPS (3000 free)
    free_iops = 3000
    costing_iops_per_instance = iops_per_instance - free_iops
    iops_total_cost = iops_cost_per_month * costing_iops_per_instance * number_of_instances * ((time / SECONDS_IN_MINUTE) / MINUTES_IN_HOUR) / (HOURS_IN_DAY * DAYS_IN_MONTH) # 3 instances for 16000 iops each

    overall_cost =  instance_total_cost + ebs_total_cost + iops_total_cost
    
    return overall_cost

def ecs_cost(time):
    # 8 vCPU, 16 GB Memory
    vCPU = 8
    memory = 16
    fargate_cpu_cost_per_vcpu = 0.04048 
    fargate_memory_cost_per_gb = 0.004445

    fargate_cpu_total_cost = fargate_cpu_cost_per_vcpu * vCPU
    fargate_memory_total_cost = fargate_memory_cost_per_gb * memory

    overall_cost = (fargate_cpu_total_cost + fargate_memory_total_cost) * ((time / SECONDS_IN_MINUTE) / MINUTES_IN_HOUR)
    return overall_cost

def calculate_experiment_duration(experiment):
    """Calculate various durations (total, indexing, retrieval, evaluation) from the experiment dictionary."""
    try:
        def calculate_difference(start_key, end_key):
            if experiment.get(start_key) and experiment.get(end_key):
                start = parse_datetime(experiment[start_key])
                end = parse_datetime(experiment[end_key])
                return (end - start).total_seconds()
            return 0

        # total_duration = calculate_difference("start_datetime", "end_datetime")
        indexing_duration = calculate_difference("indexing_start", "indexing_end")
        retrieval_duration = calculate_difference("retrieval_start", "retrieval_end")
        eval_duration = calculate_difference("eval_start", "eval_end")

        return (
            # math.ceil(total_duration / SECONDS_IN_MINUTE),
            indexing_duration,
            retrieval_duration,
            eval_duration
            # math.ceil(indexing_duration / SECONDS_IN_MINUTE),
            # math.ceil(retrieval_duration / SECONDS_IN_MINUTE),
            # math.ceil(eval_duration / SECONDS_IN_MINUTE),
        )
    except Exception as e:
        logger.error(f"Error occurred during duration computation: {e}")
        return 0, 0, 0

def calculate_experiment_question_details(experiment_question_metrics_items):
    total_questions = len(experiment_question_metrics_items)
    overall_inferencer_time = 0
    average_inferencer_time = 0
    reranker_queries = 0
    for question in experiment_question_metrics_items:
        answer_metadata = question.get("answer_metadata", None)
        if answer_metadata:
            latency = answer_metadata.get("latencyMs", 0)
            inputTokens = answer_metadata.get('inputTokens', 0)
            overall_inferencer_time += (latency / THOUSAND)
            if math.ceil(inputTokens / 500) >= 100:
                reranker_queries += (math.ceil(inputTokens / 500) / 100)
            else:
                reranker_queries += 1
    average_inferencer_time = overall_inferencer_time / total_questions
    return {
        "total_questions": total_questions,
        "overall_inferencer_time": overall_inferencer_time,
        "average_inferencer_time": average_inferencer_time,
        "reranker_queries": reranker_queries
    }

def validate_params(**kwargs):
    """
    Validates the given parameters and identifies missing ones.

    Args:
        **kwargs: Key-value pairs of parameter names and their values.

    Returns:
        tuple: A boolean indicating if there are missing parameters and a list of missing parameter names.
    """
    missing_params = [param for param, value in kwargs.items() if not value]
    return not missing_params, missing_params
