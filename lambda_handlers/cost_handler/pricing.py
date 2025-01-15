import os
import boto3
from utils import read_csv_from_s3, parse_datetime
from datetime import datetime
import math
import logging
from constants.time_constants import TimeConstants

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

s3 = boto3.client("s3")
S3_BUCKET = os.getenv("s3_bucket")
BEDROCK_CSV_PATH = os.getenv("bedrock_limit_csv")


def compute_actual_price(
    configuration, input_tokens, output_tokens, index_embed_tokens, query_embed_tokens, total_time, indexing_time, retrieval_time, eval_time
):
    """Compute the actual price based on the given configuration and token/time inputs."""

    is_input_valid, input_missing = validate_params(
        configuration=configuration,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        index_embed_tokens=index_embed_tokens,
        query_embed_tokens=query_embed_tokens,
        total_time=total_time,
        indexing_time=indexing_time,
        retrieval_time=retrieval_time,
        eval_time=eval_time
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
        aws_region = configuration.get("aws_region")
        embedding_model = configuration.get("embedding_model")
        retrieval_model = configuration.get("retrieval_model")
        embedding_service = configuration.get("embedding_service")
        retrieval_service = configuration.get("retrieval_service")

        is_config_valid, config_missing = validate_params(
            aws_region=aws_region,
            embedding_model=embedding_model,
            retrieval_model=retrieval_model,
            embedding_service=embedding_service,
            retrieval_service=retrieval_service
        )
        if not is_config_valid:
            logger.error(
                f"Configuration is missing required fields: {', '.join(config_missing)}."
            )
            return None

        indexing_cost = 0
        retrieval_cost = 0
        eval_cost = 0
        total_cost = 0

        query_embedding_cost = 0
        if embedding_service == "bedrock" :
            embedding_model_price = df[(df["model"] == embedding_model) & (df["Region"] == aws_region)]["input_price"]
            if embedding_model_price.empty:
                logger.error(f"No embedding model {embedding_model} price found.")
                return None
            embedding_model_price = float(embedding_model_price.values[0])  # Price per 1000 tokens
            indexing_cost = (embedding_model_price * float(index_embed_tokens)) / TimeConstants.THOUSAND
        else:
            indexing_cost = sagemaker_cost(indexing_time)
        
        if retrieval_service == "bedrock" :
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
            
            retrieval_model_input_actual_cost = (retrieval_model_input_price * float(input_tokens)) / TimeConstants.MILLION
            retrieval_model_output_actual_cost = (retrieval_model_output_price * float(output_tokens)) / TimeConstants.MILLION
            if embedding_service == "bedrock":
                query_embedding_cost = (embedding_model_price * float(query_embed_tokens)) / TimeConstants.THOUSAND
            retrieval_cost = retrieval_model_input_actual_cost + retrieval_model_output_actual_cost + query_embedding_cost
        else:
            retrieval_cost = sagemaker_cost(retrieval_time)
            if embedding_service == "bedrock":
                query_embedding_cost = (embedding_model_price * float(query_embed_tokens)) / TimeConstants.THOUSAND
                retrieval_cost += query_embedding_cost
            else:
                embedding_sagemaker_cost = sagemaker_cost(retrieval_time)
                retrieval_time += embedding_sagemaker_cost
            
        indexing_cost += opensearch_cost(indexing_time) + ecs_cost(indexing_time)
        retrieval_cost += opensearch_cost(retrieval_time) + ecs_cost(retrieval_time)

        eval_cost += opensearch_cost(eval_time) + ecs_cost(eval_time)
        if embedding_service == "sagemaker":
            eval_cost += sagemaker_cost(eval_time)
        if retrieval_service == "sagemaker":
            eval_cost += sagemaker_cost(eval_time)

        total_cost = indexing_cost + retrieval_cost + eval_cost
        return total_cost, indexing_cost, retrieval_cost, eval_cost
    
    except Exception as e:
        logger.error(f"Error during price computation: {e}")
        return None

def sagemaker_cost(time, number_of_instances = 1):
    instance_cost_per_hour = 1.210 #per hour ml.g5.2xlarge per model
    overall_cost = instance_cost_per_hour * number_of_instances * (time / TimeConstants.MINUTES_IN_HOUR)
    
    return overall_cost

def opensearch_cost(time):
    number_of_instances = 3

    instance_cost_per_hour = 0.711 # r7g.2xlarge.search
    instance_total_cost = (instance_cost_per_hour * number_of_instances * time / TimeConstants.MINUTES_IN_HOUR)

    ebs_volume_size = 10  # 2 GB
    ebs_volume_price_per_month = .122 
    ebs_total_cost = ebs_volume_price_per_month * ebs_volume_size * number_of_instances * (time / TimeConstants.MINUTES_IN_HOUR) / (TimeConstants.HOURS_IN_DAY * TimeConstants.DAYS_IN_MONTH) # 3 instances for 10GB each
    
    iops_cost_per_month = .008
    iops_per_instance = 16000  # instances per hour for 16000 IOPS (3000 free)
    free_iops = 3000
    costing_iops_per_instance = iops_per_instance - free_iops
    iops_total_cost = iops_cost_per_month * costing_iops_per_instance * number_of_instances * (time / TimeConstants.MINUTES_IN_HOUR) / (TimeConstants.HOURS_IN_DAY * TimeConstants.DAYS_IN_MONTH) # 3 instances for 16000 iops each

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

    overall_cost = fargate_cpu_total_cost + fargate_memory_total_cost * (time / TimeConstants.MINUTES_IN_HOUR)
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
        return 0, 0, 0, 0


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
