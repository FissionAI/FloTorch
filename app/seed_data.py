from typing import List
import logging
from fastapi import Depends

from app.dependencies.database import (
    get_execution_model_invocations_db
)

logger = logging.getLogger(__name__)

MODELS = [
    "bedrock_us.amazon.nova-lite-v1:0",
    "bedrock_us.amazon.nova-micro-v1:0",
    "bedrock_us.amazon.nova-pro-v1:0",
    "bedrock_amazon.titan-text-lite-v1",
    "bedrock_amazon.titan-text-express-v1",
    "bedrock_us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "bedrock_anthropic.claude-3-5-sonnet-20240620-v1:0",
    "bedrock_cohere.command-r-plus-v1:0",
    "bedrock_cohere.command-r-v1:0",
    "bedrock_us.meta.llama3-2-1b-instruct-v1:0",
    "bedrock_us.meta.llama3-2-3b-instruct-v1:0",
    "bedrock_us.meta.llama3-2-11b-instruct-v1:0",
    "bedrock_us.meta.llama3-2-90b-instruct-v1:0",
    "bedrock_mistral.mistral-7b-instruct-v0:2",
    "bedrock_mistral.mistral-large-2402-v1:0",
    "bedrock_amazon.titan-embed-text-v1",
    "bedrock_amazon.titan-embed-text-v2:0",
    "bedrock_amazon.titan-embed-image-v1",
    "bedrock_cohere.embed-english-v3",
    "bedrock_cohere.embed-multilingual-v3",
    "sagemaker_Qwen/Qwen2.5-32B-Instruct",
    "sagemaker_Qwen/Qwen2.5-14B-Instruct",
    "sagemaker_meta-Llama/Llama-3.1-8B",
    "sagemaker_meta-Llama/Llama-3.1-70B-Instruct",
    "sagemaker_BAAI/bge-large-en-v1.5",
    "bedrock_mistral.mixtral-8x7b-instruct-v0:1"
]

def seed_models(execution_model_invocations_db) -> None:
    """
    Seeds the models data into DynamoDB.
    
    Args:
        models_table: DynamoDBOperations instance for the models table
        
    Returns:
        Number of models seeded
    """
    try:
        for model_id in MODELS:
            execution_model_invocations_db.put_item({"execution_model_id": model_id, "invocations": 0})
                
        logger.info(f"Successfully seeded {len(MODELS)} models")
        
    except Exception as e:
        logger.error(f"Error seeding models: {str(e)}")
        raise