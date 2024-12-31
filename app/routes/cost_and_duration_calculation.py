from datetime import datetime
from util.s3util import S3Util
from config.config import get_config

configs = get_config()

S3_BUCKET = configs.s3_bucket
bedrock_price_df = S3Util().read_csv_from_s3(configs.bedrock_limit_csv_path, S3_BUCKET, as_dataframe=True)
from app.price_calculator import estimate_opensearch_price, estimate_sagemaker_price, estimate_embedding_model_bedrock_price, estimate_retrieval_model_bedrock_price
from app.configuration_validation import read_gt_data, count_characters_in_file


def calculate_experiment_duration(experiment):
    try:
        # Initialize total duration
        total_duration = 0

        # Calculate indexing duration if fields are present
        if experiment.get('indexing_start') and experiment.get('indexing_end'):
            indexing_start = datetime.strptime(experiment.get('indexing_start'), '%Y-%m-%dT%H:%M:%S.%fZ')
            indexing_end = datetime.strptime(experiment.get('indexing_end'), '%Y-%m-%dT%H:%M:%S.%fZ')
            indexing_difference = indexing_end - indexing_start
            total_duration += indexing_difference.total_seconds()

        # Calculate retrieval duration if fields are present
        if experiment.get('retrieval_start') and experiment.get('retrieval_end'):
            retrieval_start = datetime.strptime(experiment.get('retrieval_start'), '%Y-%m-%dT%H:%M:%S.%fZ')
            retrieval_end = datetime.strptime(experiment.get('retrieval_end'), '%Y-%m-%dT%H:%M:%S.%fZ')
            retrieval_difference = retrieval_end - retrieval_start
            total_duration += retrieval_difference.total_seconds()

        # Calculate eval duration if fields are present
        if experiment.get('eval_start') and experiment.get('eval_end'):
            eval_start = datetime.strptime(experiment.get('eval_start'), '%Y-%m-%dT%H:%M:%S.%fZ')
            eval_end = datetime.strptime(experiment.get('eval_end'), '%Y-%m-%dT%H:%M:%S.%fZ')
            eval_difference = eval_end - eval_start
            total_duration += eval_difference.total_seconds()

        # Return the total duration in minutes, rounded
        return round(total_duration / 60)
    except Exception as e:
        # Return 0 if any unexpected error occurs
        return 0


def calculate_experiment_cost(experiment, num_tokens_kb_data, avg_promopt_length, num_prompts, os_price):
    try:
        cost = 0
        if experiment['config']['embedding_service'] == "bedrock":

            embedding_price = estimate_embedding_model_bedrock_price(bedrock_price_df, experiment['config'],
                                                                     num_tokens_kb_data)
            cost += embedding_price
        else:
            cost += estimate_sagemaker_price()

        if experiment['config']["retrieval_service"] == "bedrock":
            retrical_price = estimate_retrieval_model_bedrock_price(bedrock_price_df, experiment['config'],
                                                                    avg_promopt_length,
                                                                    num_prompts)
            cost += retrical_price
        else:
            cost += estimate_sagemaker_price()
        cost += os_price
        cost += cost * 0.2  # extra
        cost = round(cost, 2)
        return cost
    except Exception as e:
        return 0



def calculate_duration(response):
    try:
        final_response = []
        for each_item in response:
            if 'experiment_status' in each_item and each_item['experiment_status'] in ['succeeded','failed']:
                each_item['total_time'] = calculate_experiment_duration(each_item)
            else:
                each_item['total_time'] = 0
            final_response.append(each_item)
        return final_response
    except Exception as e:
        return response


def calculate_cost(response):
    try:
        final_response = []
        os_price = estimate_opensearch_price()
        if response:
            num_tokens_kb_data = count_characters_in_file(response[0]['config']["kb_data"]) / 4
            gt_data = response[0]['config']["gt_data"]
            [num_prompts, num_chars] = read_gt_data(gt_data)

            avg_promopt_length = round(num_chars / num_prompts / 4)
            for each_item in response:
                cost = calculate_experiment_cost(each_item, num_tokens_kb_data, avg_promopt_length, num_prompts, os_price)
                each_item['cost'] = cost
                final_response.append(each_item)
            return final_response
        else:
            return response
    except Exception as e:
        return response