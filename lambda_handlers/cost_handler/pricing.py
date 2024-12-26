import os
import boto3
from utils import read_csv_from_s3
from datetime import datetime
import math
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

s3 = boto3.client("s3")
S3_BUCKET = os.getenv("s3_bucket")
BEDROCK_CSV_PATH = os.getenv("bedrock_limit_csv")

# Constants
MILLION = 1_000_000
THOUSAND = 1_000
SECONDS_IN_MINUTE = 60


def compute_actual_price(
    configuration, input_tokens, output_tokens, embed_tokens, os_time, ecs_time
):
    """Compute the actual price based on the given configuration and token/time inputs."""

    is_input_valid, input_missing = validate_params(
        configuration=configuration,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        embed_tokens=embed_tokens,
        os_time=os_time,
        ecs_time=ecs_time,
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

        is_config_valid, config_missing = validate_params(
            aws_region=aws_region,
            embedding_model=embedding_model,
            retrieval_model=retrieval_model,
        )
        if not is_config_valid:
            logger.error(
                f"Configuration is missing required fields: {', '.join(config_missing)}."
            )
            return None

        embedding_model_price = df[
            (df["model"] == embedding_model) & (df["Region"] == aws_region)
        ]["input_price"]
        retrieval_model_input_price = df[
            (df["model"] == retrieval_model) & (df["Region"] == aws_region)
        ]["input_price"]
        retrieval_model_output_price = df[
            (df["model"] == retrieval_model) & (df["Region"] == aws_region)
        ]["output_price"]

        is_prices_present, prices_missing = validate_params(
            embedding_model_price=embedding_model_price,
            retrieval_model_input_price=retrieval_model_input_price,
            retrieval_model_output_price=retrieval_model_output_price,
        )

        if not is_prices_present:
            logger.error(
                f"No matching price data found for the provided models : {', '.join(prices_missing)}."
            )
            return None

        embedding_model_price = float(
            embedding_model_price.values[0]
        )  # Price per 1000 tokens
        retrieval_model_input_price = float(
            retrieval_model_input_price.values[0]
        )  # Price per million tokens
        retrieval_model_output_price = float(
            retrieval_model_output_price.values[0]
        )  # Price per million tokens

        # Calculate costs
        embedding_actual_cost = (embedding_model_price * float(embed_tokens)) / THOUSAND
        retrieval_model_input_actual_cost = (
            retrieval_model_input_price * float(input_tokens)
        ) / MILLION
        retrieval_model_output_actual_cost = (
            retrieval_model_output_price * float(output_tokens)
        ) / MILLION

        opensearch_actual_cost = (0.711 * 3 * os_time / SECONDS_IN_MINUTE) + (
            (0.122 * 2 * os_time + 13000 * 0.008 * os_time) / (30 * 24)
        ) / SECONDS_IN_MINUTE
        ecs_actual_cost = (
            0.04048 * 8 * ecs_time + 0.004445 * 16 * ecs_time
        ) / SECONDS_IN_MINUTE

        total_actual_cost = (
            embedding_actual_cost
            + retrieval_model_input_actual_cost
            + retrieval_model_output_actual_cost
            + opensearch_actual_cost
            + ecs_actual_cost
        )

        return total_actual_cost
    except Exception as e:
        logger.error(f"Error during price computation: {e}")
        return None


def calculate_experiment_duration(experiment):
    """Calculate various durations (total, indexing, retrieval, evaluation) from the experiment dictionary."""
    try:

        def parse_datetime(date_str):
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")

        def calculate_difference(start_key, end_key):
            if experiment.get(start_key) and experiment.get(end_key):
                start = parse_datetime(experiment[start_key])
                end = parse_datetime(experiment[end_key])
                return (end - start).total_seconds()
            return 0

        total_duration = calculate_difference("start_datetime", "end_datetime")
        indexing_duration = calculate_difference("indexing_start", "indexing_end")
        retrieval_duration = calculate_difference("retrieval_start", "retrieval_end")
        eval_duration = calculate_difference("eval_start", "eval_end")

        return (
            math.ceil(total_duration / SECONDS_IN_MINUTE),
            math.ceil(indexing_duration / SECONDS_IN_MINUTE),
            math.ceil(retrieval_duration / SECONDS_IN_MINUTE),
            math.ceil(eval_duration / SECONDS_IN_MINUTE),
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
