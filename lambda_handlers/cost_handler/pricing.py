import os
import boto3
from utils import read_csv_from_s3
from datetime import datetime

import logging
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

s3 = boto3.client('s3') 
S3_BUCKET = os.getenv('s3_bucket')
BEDROCK_CSV_PATH = os.getenv('bedrock_limit_csv')

def compute_actual_price(configuration, input_tokens, output_tokens, embed_tokens, os_time, ecs_time):
    try:
        df = read_csv_from_s3(BEDROCK_CSV_PATH, S3_BUCKET)
        # return df
    except Exception as e:
        logger.error(f"Error reading the CSV file: {e}")
        return None

    region = configuration["aws_region"]
    embed_model = configuration["embedding_model"]
    gen_model = configuration["retrieval_model"]

    embed_model_price = df[(df['model'] == embed_model) & (df['Region'] == region)]['input_price']
    embed_model_price = float(embed_model_price.values[0]) #this price is in 1000s of tokens not millions

    gen_model_price = df[(df['model'] == gen_model) & (df['Region'] == region)]['input_price']
    gen_model_price = float(gen_model_price.values[0]) #this price is in millions of tokens

    gen_model_out_price = df[(df['model'] == gen_model) & (df['Region'] == region)]['output_price']
    gen_model_out_price = float(gen_model_out_price.values[0]) #this price is in millions of tokens

    embed_actual_price = (embed_model_price * float(embed_tokens)) / 1000
    gen_in_actual_price = (gen_model_price * float(input_tokens)) / 1000000
    gen_out_actual_price = (gen_model_out_price * float(output_tokens)) / 1000000

    os_actual_price = (.711 * 3 * os_time / 60) + ((.122 * 2 * os_time + 13000 * .008 * os_time) / 30 / 24) /60
    ecs_actual_price = (0.04048 * 8 * ecs_time + 0.004445 * 16 * ecs_time) / 60

    total_actual_price = embed_actual_price + gen_in_actual_price + gen_out_actual_price + os_actual_price + ecs_actual_price

    return total_actual_price

def calculate_experiment_duration(experiment):
    try:
        # Initialize total duration
        total_duration = 0
        indexing_difference = 0
        retrieval_difference = 0
        eval_difference = 0

        # Calculate total duration if fields are present
        if experiment.get('start_datetime') and experiment.get('end_datetime'):
            experiment_start = datetime.strptime(experiment.get('start_datetime'), '%Y-%m-%dT%H:%M:%S.%fZ')
            experiment_end = datetime.strptime(experiment.get('end_datetime'), '%Y-%m-%dT%H:%M:%S.%fZ')
            experiment_difference = experiment_end - experiment_start
            total_duration = experiment_difference.total_seconds()

        # Calculate indexing duration if fields are present
        if experiment.get('indexing_start') and experiment.get('indexing_end'):
            indexing_start = datetime.strptime(experiment.get('indexing_start'), '%Y-%m-%dT%H:%M:%S.%fZ')
            indexing_end = datetime.strptime(experiment.get('indexing_end'), '%Y-%m-%dT%H:%M:%S.%fZ')
            indexing_difference = indexing_end - indexing_start
            indexing_difference = indexing_difference.total_seconds()

        # Calculate retrieval duration if fields are present
        if experiment.get('retrieval_start') and experiment.get('retrieval_end'):
            retrieval_start = datetime.strptime(experiment.get('retrieval_start'), '%Y-%m-%dT%H:%M:%S.%fZ')
            retrieval_end = datetime.strptime(experiment.get('retrieval_end'), '%Y-%m-%dT%H:%M:%S.%fZ')
            retrieval_difference = retrieval_end - retrieval_start
            retrieval_difference = retrieval_difference.total_seconds()

        # Calculate eval duration if fields are present
        if experiment.get('eval_start') and experiment.get('eval_end'):
            eval_start = datetime.strptime(experiment.get('eval_start'), '%Y-%m-%dT%H:%M:%S.%fZ')
            eval_end = datetime.strptime(experiment.get('eval_end'), '%Y-%m-%dT%H:%M:%S.%fZ')
            eval_difference = eval_end - eval_start
            eval_difference = eval_difference.total_seconds()

        # Return the total duration in minutes, rounded
        return round(total_duration / 60),round(indexing_difference / 60),round(retrieval_difference / 60),round(eval_difference / 60)
    except Exception as e:
        logger.error(f"Error occured during time computation : {e}")
        # Return 0 if any unexpected error occurs
        return 0
