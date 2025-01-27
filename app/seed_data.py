import logging
from fastapi import Depends

from app.dependencies.database import (
    get_execution_model_invocations_db
)

logger = logging.getLogger(__name__)

MODELS = {
    "bedrock_us.amazon.nova-lite-v1:0": 35,
    "bedrock_us.amazon.nova-micro-v1:0": 35,
    "bedrock_us.amazon.nova-pro-v1:0": 12,
    "bedrock_amazon.titan-text-lite-v1": 14,
    "bedrock_amazon.titan-text-express-v1": 14,
    "bedrock_us.anthropic.claude-3-5-sonnet-20241022-v2:0": 5,
    "bedrock_anthropic.claude-3-5-sonnet-20240620-v1:0": 5,
    "bedrock_cohere.command-r-plus-v1:0": 25,
    "bedrock_cohere.command-r-v1:0": 14,
    "bedrock_us.meta.llama3-2-1b-instruct-v1:0": 14,
    "bedrock_us.meta.llama3-2-3b-instruct-v1:0": 14,
    "bedrock_us.meta.llama3-2-11b-instruct-v1:0": 14,
    "bedrock_us.meta.llama3-2-90b-instruct-v1:0": 25,
    "bedrock_mistral.mistral-7b-instruct-v0:2": 25,
    "bedrock_mistral.mistral-large-2402-v1:0": 25,
    "bedrock_amazon.titan-embed-text-v1": 30,
    "bedrock_amazon.titan-embed-text-v2:0": 30,
    "bedrock_amazon.titan-embed-image-v1": 30,
    "bedrock_cohere.embed-english-v3": 30,
    "bedrock_cohere.embed-multilingual-v3": 30,
    "sagemaker_Qwen/Qwen2.5-32B-Instruct": 50,
    "sagemaker_Qwen/Qwen2.5-14B-Instruct": 50,
    "sagemaker_meta-Llama/Llama-3.1-8B": 50,
    "sagemaker_meta-Llama/Llama-3.1-70B-Instruct": 50,
    "sagemaker_BAAI/bge-large-en-v1.5": 50,
    "bedrock_mistral.mixtral-8x7b-instruct-v0:1": 25,
    "sagemaker_huggingface-sentencesimilarity-bge-large-en-v1-5": 4,
    "sagemaker_huggingface-sentencesimilarity-bge-m3": 4,
    "sagemaker_huggingface-textembedding-gte-qwen2-7b-instruct": 2,
    "sagemaker_meta-textgeneration-llama-3-1-8b-instruct": 2,
    "sagemaker_huggingface-llm-falcon-7b-instruct-bf16": 2,
    "sagemaker_meta-textgeneration-llama-3-3-70b-instruct": 4,
    "sagemaker_deepseek-ai/DeepSeek-R1-Distill-Llama-8B": 2
}

def seed_models(execution_model_invocations_db) -> int:
    """
    Seeds the models data into DynamoDB.
    
    Args:
        execution_model_invocations_db: DynamoDBOperations instance for the models table
        
    Returns:
        int: Number of models seeded
    
    Raises:
        Exception: If there's an error during seeding
    """
    try:
        if not execution_model_invocations_db:
            raise ValueError("Database connection is required")

        seeded_count = 0
        for model_id, model_limit in MODELS.items():
            if not model_limit or model_limit <= 0:
                logger.error(f"Model limit {model_limit} is invalid for {model_id}")
                model_limit = 5
            execution_model_invocations_db.put_item({
                "execution_model_id": model_id, 
                "invocations": 0, 
                "limit": model_limit
            })
            seeded_count += 1
                
        logger.info(f"Successfully seeded {seeded_count} models")
        return seeded_count
        
    except Exception as e:
        logger.error(f"Error seeding models: {str(e)}")
        raise