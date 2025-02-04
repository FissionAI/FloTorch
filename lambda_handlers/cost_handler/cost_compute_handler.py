import boto3
import json
import os
from pricing import compute_actual_price_breakdown, calculate_experiment_duration
from decimal import Decimal
import math

import logging
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

MILLION = 1_000_000
THOUSAND = 1_000
SECONDS_IN_MINUTE = 60
MINUTES_IN_HOUR = 60
HOURS_IN_DAY = 24
DAYS_IN_MONTH = 30

# Initialize AWS services clients
dynamodb = boto3.resource("dynamodb")


def fetch_data_from_dynamodb(table_name, key, value, index_name=None):
    """
    Fetch items with the specified key and value from DynamoDB.
    """
    try:
        table = dynamodb.Table(table_name)
        query_params = {
            "KeyConditionExpression": boto3.dynamodb.conditions.Key(key).eq(value)
        }
        if index_name:
            query_params["IndexName"] = index_name
        response = table.query(**query_params)
        return response.get("Items", [])
    except Exception as e:
        logger.error(f"Error fetching data from DynamoDB: {e}")
        raise


def validate_event(event):
    """
    Validate the input event to ensure required fields are present.
    """
    required_fields = ["experiment_id"]
    for field in required_fields:
        if field not in event:
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(event["experiment_id"], str):
        raise ValueError("'experiment_id' must be a string")


def lambda_handler(event, context):
    """
    Lambda handler function.
    """
    try:
        logger.info(f"Experiment Configuration received: {event}")

        # Validate input event
        validate_event(event)

        experiment_id = event["experiment_id"]
        experiment_table = os.getenv("experiment_table")
        experiment_question_metrics_table = os.getenv("experiment_question_metrics_table")
        experiment_question_metrics_index = os.getenv("experiment_question_metrics_index")

        if not experiment_table:
            raise EnvironmentError("Environment variable 'experiment_table' is not set")
        
        if not experiment_question_metrics_table:
            raise EnvironmentError("Environment variable 'experiment_question_metrics_table' is not set")
        
        # Initialize variables
        total_query_embed_tokens = 0
        total_answer_input_tokens = 0
        total_answer_output_tokens = 0

        experiment_items = fetch_data_from_dynamodb(experiment_table, 'id', experiment_id)
        experiment_question_metrics_items = fetch_data_from_dynamodb(experiment_question_metrics_table, 'experiment_id', experiment_id, experiment_question_metrics_index)
        total_duration = 0
        indexing_time = 0
        retrieval_time = 0
        eval_time = 0
        total_index_embed_tokens = 0

        if experiment_items:
            experiment = experiment_items[0]
            indexing_time, retrieval_time, eval_time = calculate_experiment_duration(experiment)
            indexing_time_in_min = math.ceil(indexing_time / SECONDS_IN_MINUTE)
            retrieval_time_in_min = math.ceil(retrieval_time / SECONDS_IN_MINUTE)
            eval_time_in_min = math.ceil(eval_time / SECONDS_IN_MINUTE)
            total_duration = indexing_time + retrieval_time + eval_time
            total_duration_in_min = indexing_time_in_min + retrieval_time_in_min + eval_time_in_min
            logger.info(f"Experiment {experiment_id} Total Time (in minutes): {total_duration_in_min} Indexing Time: {indexing_time_in_min}, Retrieval: {retrieval_time_in_min}, Evaluation: {eval_time_in_min}")

            total_index_embed_tokens = experiment.get("index_embed_tokens", 0)
            total_query_embed_tokens = experiment.get("retrieval_query_embed_tokens", 0)
            total_answer_input_tokens = experiment.get("retrieval_input_tokens", 0)
            total_answer_output_tokens = experiment.get("retrieval_output_tokens", 0)

        overall_metadata, indexing_metadata, retriever_metadata, inferencer_metadata, eval_metadata = compute_actual_price_breakdown(
            experiment,
            input_tokens=total_answer_input_tokens,
            output_tokens=total_answer_output_tokens,
            index_embed_tokens=total_index_embed_tokens,
            query_embed_tokens=total_query_embed_tokens,
            total_time=total_duration_in_min,
            indexing_time=indexing_time_in_min,
            retrieval_time=retrieval_time_in_min,
            eval_time=eval_time_in_min,
            experiment_question_metrics_items=experiment_question_metrics_items
        )

        total_cost = overall_metadata['total_cost']
        indexing_cost = indexing_metadata['total_cost']
        retriever_cost = retriever_metadata['total_cost']
        inferencer_cost = inferencer_metadata['total_cost']
        eval_cost = eval_metadata['total_cost']
        logger.info(f"Experiment {experiment_id} Actual Cost (in $): {total_cost}, Indexing: {indexing_cost}, Retrieval: {retriever_cost}, Inferencing: {inferencer_cost}, Evaluation : {eval_cost}")

        # Update DynamoDB with the new cost
        if total_cost is None:
            logger.error(f"Experiment {experiment_id} Actual Cost is None")
            total_cost = 0

        try:
            table = dynamodb.Table(experiment_table)
            table.update_item(
                Key={"id": experiment_id},
                UpdateExpression="SET cost = :new_cost, indexing_time = :new_indexing_time, retrieval_time = :new_retrieval_time, eval_time = :new_eval_time, total_time = :new_total_time, indexing_cost = :new_indexing_cost, retrieval_cost = :new_retrieval_cost, inferencing_cost = :new_inferencing_cost, eval_cost = :new_eval_cost, indexing_metadata = :new_indexing_metadata, retriever_metadata = :new_retriever_metadata, inferencer_metadata = :new_inferencer_metadata, eval_metadata = :new_eval_metadata, overall_metadata = :new_overall_metadata",
                ExpressionAttributeValues={
                    ":new_cost": str(total_cost),
                    ":new_indexing_cost": str(indexing_cost),
                    ":new_retrieval_cost": str(retriever_cost),
                    ":new_inferencing_cost": str(inferencer_cost),
                    ":new_eval_cost": str(eval_cost),
                    ":new_indexing_time": str(indexing_time),
                    ":new_retrieval_time": str(retrieval_time),
                    ":new_eval_time": str(eval_time),
                    ":new_total_time": str(total_duration),
                    ":new_indexing_metadata": indexing_metadata,
                    ":new_retriever_metadata": retriever_metadata,
                    ":new_inferencer_metadata": inferencer_metadata,
                    ":new_eval_metadata": eval_metadata,
                    ":new_overall_metadata": overall_metadata
                },
            )
        except Exception as e:
            logger.error(f"Error updating DynamoDB: {e}")
            raise

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "total_cost": total_cost,
                    "dynamodb_update_count": len(experiment_items),
                }
            ),
        }

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return {"statusCode": 400, "body": json.dumps({"error": str(ve)})}
    except EnvironmentError as ee:
        logger.error(f"Environment error: {ee}")
        return {"statusCode": 500, "body": json.dumps({"error": str(ee)})}
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
        }
