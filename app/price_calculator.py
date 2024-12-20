import pandas as pd
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def estimate_embedding_model_bedrock_price(file_path, configuration, num_tokens_kb_data):
    try:
        df = file_path.copy()
        # return df
    except Exception as e:
        logger.error(f"Error reading the CSV file: {e}")
        return None
    region = configuration["region"]
    chunk_size = configuration["chunk_size"]
    chunk_overlap = configuration["chunk_overlap"]
    embed_model = configuration["embedding_model"]

    eff_chunk_size = chunk_size * (1 - chunk_overlap / 100)

    num_chunks = num_tokens_kb_data / float(eff_chunk_size)
    num_tokens_with_overlap = num_chunks * float(eff_chunk_size)
    embed_model_price = df[(df['model'] == embed_model) & (df['Region'] == region)]['input_price']
    if embed_model_price.empty:
        logger.warning("Returning price as Zero, as model is not present in Sheet")
        return 0
    else:
        embed_model_price = float(embed_model_price.values[0])  # this price is in 1000s of tokens not millions
        embed_price = embed_model_price * num_tokens_with_overlap / 1000000
        return embed_price


def estimate_retrieval_model_bedrock_price(file_path, configuration, avg_prompt_length,
                                           num_prompts):
    try:
        df = file_path.copy()
        # return df
    except Exception as e:
        logger.error(f"Error reading the CSV file: {e}")
        return None
    region = configuration["region"]
    chunk_size = configuration["chunk_size"]
    gen_model = configuration["retrieval_model"]
    n_shot_prompts = configuration["n_shot_prompts"]
    k = configuration["knn_num"]

    gen_model_price = df[(df['model'] == gen_model) & (df['Region'] == region)]['input_price']
    if gen_model_price.empty:
        logger.warning("Returning price as Zero, as model is not present in Sheet")
        return 0
    else:
        gen_model_price = float(gen_model_price.values[0])  # this price is in millions of tokens
        gen_model_out_price = df[(df['model'] == gen_model) & (df['Region'] == region)]['output_price']
        gen_model_out_price = float(gen_model_out_price.values[0])  # this price is in millions of tokens
        context_len = k * chunk_size
        prompt_len = (n_shot_prompts + 1) * avg_prompt_length
        total_input_tokens = (context_len + prompt_len) * num_prompts
        retrieval_input_price = gen_model_price * float(total_input_tokens) / 1000000
        total_output_tokens = avg_prompt_length
        retrieval_output_price = gen_model_out_price * float(total_output_tokens) / 1000000
        retrieval_price = retrieval_input_price + retrieval_output_price
        return retrieval_price



def calculate_fargate_price(vpc,mem,total_time,num_exps,num_instance):
    #Fargate pricing
    fargate_cpu = 0.04048 
    fargate_mem = 0.004445
    fargate_cpu_price = fargate_cpu * num_instance * vpc
    fargate_mem_price = fargate_mem * num_instance * mem

    fargate_price = (fargate_cpu_price + fargate_mem_price) * total_time / 3600 / num_exps
    return fargate_price
    
def estimate_opensearch_price(num_exps, num_prompts, num_chunks=1, max_rpm=20):
    opensearch_instance_cost_per_hour = .711
    num_instance = 3
    instance_price =  opensearch_instance_cost_per_hour * num_instance #per hour
    ebs_volume_size = 2
    ebs_volume_price = .122
    ebs_price = ebs_volume_price * ebs_volume_size * num_instance /30 /24 #3 instances for 2GB per hour
    iops_price_per_hour = 13000  # instances per hour for 16000 IOPS (3000 free)
    iops_price = iops_price_per_hour * .008 * num_instance /30/ 24 #3 instances
    #rps = 751 #100 threads running in parallel
    rps = float(max_rpm/60) # 20 threads running in parallel

    total_requests = num_exps * num_prompts
    total_time = float(total_requests) / rps
    total_os_price = (instance_price + ebs_price + iops_price) * total_time / 3600  #price per experiment

    #Fargate pricing
    vpc=8 # 8vpc
    mem=16 #16GB memory
    total_fargate_price = calculate_fargate_price(vpc,mem,total_time,num_exps,num_instance)
    total_price = total_os_price + total_fargate_price

    return total_price

def estimate_sagemaker_price():
    sagemaker_price = 1.515 #per hour g5.2xlarge per model
    number_of_instances = 1
    number_of_hrs = 3
    num_models=1
    overall_cost = sagemaker_price * number_of_instances * number_of_hrs*num_models
    
    return overall_cost