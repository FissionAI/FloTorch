import boto3
import json
import os
from pricing import compute_actual_price, calculate_experiment_duration

import logging
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

# Initialize AWS services clients
dynamodb = boto3.resource('dynamodb')

def fetch_from_dynamodb(experiment_id, table_name):
    """
    Fetch items with the specified experiment_id from DynamoDB.
    """
    table = dynamodb.Table(table_name)
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('id').eq(experiment_id)
    )
    return response.get('Items', [])

def lambda_handler(event, context):
    """
    Lambda handler function.
    """
    logger.info(f"Experiment Configuration received : {event}")
    experiment_id = event['experiment_id']
    # index_id = event['index_id']
    experiment_table = os.getenv('experiment_table')

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
        logger.info(f"Experiment {experiment_id} Total Time (in minutes) : {total_duration}, Indexing Time : {indexing_time}, Retrieval : {retrieval_time}, Evaluation : {eval_time}")
        total_index_embed_tokens = experiment.get('index_embed_tokens')
        total_query_embed_tokens = experiment.get('retrieval_query_embed_tokens')
        total_answer_input_tokens = experiment.get('retrieval_input_tokens')
        total_answer_output_tokens = experiment.get('retrieval_output_tokens')

    total_ecs_time = indexing_time + retrieval_time + eval_time
    logger.info(f"Experiment {experiment_id} Total ECS Time : {total_ecs_time}")
    total_embed_tokens = total_index_embed_tokens + total_query_embed_tokens
    total_cost = compute_actual_price(event, input_tokens=total_answer_input_tokens, output_tokens=total_answer_output_tokens, embed_tokens=total_embed_tokens, os_time=total_duration, ecs_time=total_ecs_time)   

    logger.info(f"Experiment {experiment_id} Actual Cost (in $) : {total_cost}")
    # Update DynamoDB with the new cost
    table = dynamodb.Table(experiment_table)
    table.update_item(
        Key={
            'id': experiment_id
        },
        UpdateExpression="SET cost = :new_cost, indexing_time = :new_indexing_time, retrieval_time = :new_retrieval_time, eval_time = :new_eval_time",
        ExpressionAttributeValues={":new_cost": str(total_cost), ":new_indexing_time": indexing_time, ":new_retrieval_time": retrieval_time, ":new_eval_time": eval_time}
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'total_cost': total_cost,
            'dynamodb_update_count': len(experiment_items)
        })
    }