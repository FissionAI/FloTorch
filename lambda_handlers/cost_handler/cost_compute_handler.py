import boto3
import json
import os
from pricing import compute_actual_price, calculate_experiment_duration

import logging
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

# Initialize AWS services clients
dynamodb = boto3.resource("dynamodb")


def fetch_from_dynamodb(experiment_id, table_name):
    """
    Fetch items with the specified experiment_id from DynamoDB.
    """
    try:
        table = dynamodb.Table(table_name)
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("id").eq(experiment_id)
        )
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

        if not experiment_table:
            raise EnvironmentError("Environment variable 'experiment_table' is not set")

        # Initialize variables
        total_query_embed_tokens = 0
        total_answer_input_tokens = 0
        total_answer_output_tokens = 0

        experiment_items = fetch_from_dynamodb(experiment_id, experiment_table)
        total_duration = 0
        indexing_time = 0
        retrieval_time = 0
        eval_time = 0
        total_index_embed_tokens = 0

        if experiment_items:
            experiment = experiment_items[0]
            total_duration, indexing_time, retrieval_time, eval_time = calculate_experiment_duration(experiment)

            logger.info(f"Experiment {experiment_id} Total Time (in minutes): {total_duration} Indexing Time: {indexing_time}, Retrieval: {retrieval_time}, Evaluation: {eval_time}")

            total_index_embed_tokens = experiment.get("index_embed_tokens", 0)
            total_query_embed_tokens = experiment.get("retrieval_query_embed_tokens", 0)
            total_answer_input_tokens = experiment.get("retrieval_input_tokens", 0)
            total_answer_output_tokens = experiment.get("retrieval_output_tokens", 0)

        # Compute total ECS time and cost
        total_ecs_time = indexing_time + retrieval_time + eval_time
        logger.info(f"Experiment {experiment_id} Total ECS Time : {total_ecs_time}")
        total_embed_tokens = total_index_embed_tokens + total_query_embed_tokens

        total_cost = compute_actual_price(
            event,
            input_tokens=total_answer_input_tokens,
            output_tokens=total_answer_output_tokens,
            embed_tokens=total_embed_tokens,
            os_time=total_duration,
            ecs_time=total_ecs_time,
        )

        logger.info(f"Experiment {experiment_id} Actual Cost (in $): {total_cost}")

        # Update DynamoDB with the new cost
        try:
            table = dynamodb.Table(experiment_table)
            table.update_item(
                Key={"id": experiment_id},
                UpdateExpression="SET cost = :new_cost, indexing_time = :new_indexing_time, retrieval_time = :new_retrieval_time, eval_time = :new_eval_time",
                ExpressionAttributeValues={
                    ":new_cost": str(total_cost),
                    ":new_indexing_time": indexing_time,
                    ":new_retrieval_time": retrieval_time,
                    ":new_eval_time": eval_time,
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
