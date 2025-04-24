from typing import List, Dict
from pydantic import BaseModel, RootModel
import logging
import asyncio

from http.client import HTTPException

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from config.config import get_config
from util.s3util import S3Util

from flotorch_core.inferencer.inferencer_provider_factory import InferencerProviderFactory
from flotorch_core.storage.db.vector.vector_storage_factory import VectorStorageFactory
from flotorch_core.embedding.embedding_registry import embedding_registry
from flotorch_core.storage.db.dynamodb import DynamoDB
from flotorch_core.config.config import Config
from flotorch_core.config.env_config_provider import EnvConfigProvider
from flotorch_core.chunking.chunking import Chunk

from flotorch_core.embedding.titanv2_embedding import TitanV2Embedding
from flotorch_core.embedding.titanv1_embedding import TitanV1Embedding
from flotorch_core.embedding.cohere_embedding import CohereEmbedding
from flotorch_core.embedding.bge_large_embedding import BGELargeEmbedding, BGEM3Embedding, GTEQwen2Embedding

# Flotorch-core config
env_config_provider = EnvConfigProvider()
config = Config(env_config_provider)

configs = get_config()
S3_BUCKET = configs.s3_bucket

logger = logging.getLogger(__name__)
router = APIRouter()

bedrock_price_df = S3Util().read_csv_from_s3(configs.bedrock_limit_csv_path, S3_BUCKET, as_dataframe=True)

class ExperimentQuery(BaseModel):
    experiment_ids: List[str]
    query: str
    
class VotePayload(RootModel):
    root: Dict[str, int]
    
    
def get_model_question_prices(file_path, model, input_tokens, output_tokens, region):
    """
    Calculate the cost of model inference for a given number of input and output tokens.
    
    Args:
        file_path: DataFrame containing pricing information
        model: Name of the model being used
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens  
        region: AWS region
        
    Returns:
        Tuple containing:
        - Cost per question
        - Cost per million questions
        Or None if there's an error
    """
    MILLION = 1_000_000
    try:
        if '/' in model:
            model = model.split('/')[1]
        # Create copy of pricing dataframe
        df = file_path.copy()
        
        # Get input price for model and region
        retrieval_model_input_price = df[(df['model'] == model) & (df['Region'] == region)]['input_price']
        if retrieval_model_input_price.empty:
            logger.warning("Returning price as Zero, as model is not present in Sheet")
            return 0, 0
        else:
            # Get output price for model and region
            retrieval_model_input_price = float(retrieval_model_input_price.values[0])  # this price is in millions of tokens
            retrieval_model_output_price = df[(df['model'] == model) & (df['Region'] == region)]['output_price']
            retrieval_model_output_price = float(retrieval_model_output_price.values[0])  # this price is in millions of tokens
            
            # Calculate input and output costs based on token counts
            retrieval_model_input_actual_cost = (retrieval_model_input_price * float(input_tokens))
            retrieval_model_output_actual_cost = (retrieval_model_output_price * float(output_tokens))
            
            # Calculate total costs for a single question and a million questions
            total_cost_per_million_questions = retrieval_model_input_actual_cost + retrieval_model_output_actual_cost
            total_cost_for_question = total_cost_per_million_questions/MILLION
            return total_cost_for_question, total_cost_per_million_questions
        
    except Exception as e:
        logger.error(f"Error reading the CSV file: {e}")
        return None
    
    
def get_experiment_db():
    return DynamoDB(config.get_experiment_table_name())

def get_experiment_configs(experiment_db: DynamoDB, experiment_ids: List[str]) -> List[Dict]:
    """
    Get the experiment configs for all experiments using their IDs.

    Args:
        experiment_db: Instance of DynamoDB.
        experiment_ids (List[str]): List of experiment IDs.

    Returns:
        List[Dict]: List of JSON objects for each experiment.
    """
    experiments = []
    for experiment_id in experiment_ids:
        try:
            item = experiment_db.read({'id': experiment_id})
            if item:
                experiments.append(item)
        except Exception as e:
            print(f"Error reading from DynamoDB for ID {experiment_id}: {str(e)}")
    return experiments


@router.post("/heval/query-experiments", tags=["heval"])
async def query_experiments(
    query: ExperimentQuery,
    experiment_db: DynamoDB = Depends(get_experiment_db)
):
    num_experiments = len(query.experiment_ids)
    if not (2 <= num_experiments <= 3):
        raise HTTPException(
            status_code=400,
            detail="The number of experiment_ids must be between 2 and 3."
        )

    experiment_configs = get_experiment_configs(experiment_db, query.experiment_ids)

    async def run_experiment(exp_config_data):
        experiment_id = exp_config_data.get("id")
        exp_config = exp_config_data.get("config")

        # Configurations        
        inference_model = exp_config.get("retrieval_model")
        inference_service = exp_config.get("retrieval_service")
        inference_temperature = float(exp_config.get("temp_retrieval_llm", 0.1))

        aws_region = exp_config.get("region")
        knowledge_base = exp_config.get("knowledge_base", False)
        bedrock_knowledge_base = exp_config.get("bedrock_knowledge_base", False)
        gateway_url = f'{exp_config.get("gateway_url", "")}/api/openai/v1'

        # Inferencer Initialization
        inferencer = InferencerProviderFactory.create_inferencer_provider(
            exp_config.get("gateway_enabled"),
            gateway_url,
            exp_config.get("gateway_api_key", ""),
            inference_service,
            inference_model,
            aws_region,
            config.get_sagemaker_arn_role(),
            int(exp_config.get("n_shot_prompts")),
            inference_temperature,
            exp_config.get("n_shot_prompt_guide")
        )

        vector_storage = None
        if knowledge_base:
            vector_storage = VectorStorageFactory.create_vector_storage(
                knowledge_base=knowledge_base,
                use_bedrock_kb=bedrock_knowledge_base,
                embedding=(
                    embedding_registry.get_model(exp_config.get("embedding_model"))(
                        exp_config.get("embedding_model"), aws_region, 
                        int(exp_config.get("vector_dimension"))
                    )
                    if not bedrock_knowledge_base else None
                ),
                **(
                    {
                        "opensearch_host": config.get_opensearch_host(),
                        "opensearch_port": config.get_opensearch_port(),
                        "opensearch_username": config.get_opensearch_username(),
                        "opensearch_password": config.get_opensearch_password(),
                        "index_id": exp_config_data.get("index_id"),
                    } if not bedrock_knowledge_base else {}
                ),
                knowledge_base_id=exp_config.get("kb_data"),
                aws_region=aws_region
            )

        # Answer Generation
        if vector_storage:
            hierarchical = exp_config.get("chunking_strategy") == 'hierarchical'
            question_chunk = Chunk(data=query.query)

            vector_response = await asyncio.to_thread(
                vector_storage.search, question_chunk, int(exp_config['knn_num']), hierarchical
            )
            vector_response = vector_response.to_json()['result']
            metadata, answer = await asyncio.to_thread(
                inferencer.generate_text, query.query, vector_response
            )
        else:
            metadata, answer = await asyncio.to_thread(
                inferencer.generate_text, query.query, None
            )
            
        input_tokens, output_tokens, total_tokens, latency = metadata.values()
        question_price, million_questions_price = get_model_question_prices(bedrock_price_df, inference_model, input_tokens, output_tokens, aws_region)
        
        metadata['total_token_price'] = question_price
        metadata['million_question_price'] = million_questions_price

        return {
            "experiment_id": experiment_id,
            "inference_model": inference_model,
            "temperature": inference_temperature,
            "answer": answer,
            "metadata": metadata
        }

    results = await asyncio.gather(*[run_experiment(exp) for exp in experiment_configs])

    return JSONResponse(content={"results": results})

    
@router.post("/heval/upvote", tags=["heval"])
async def vote(
    vote_data: VotePayload,
    experiment_db: DynamoDB = Depends(get_experiment_db)
    ):
    
    # Validate payload is not empty
    votes = vote_data.root
    if not votes:
        raise HTTPException(status_code=400, detail="Vote payload cannot be empty")
        
    results = {}
    
    try:
        for exp_id, vote in votes.items():
            # Validate experiment ID is not empty
            if not exp_id:
                raise HTTPException(status_code=400, detail="Experiment ID cannot be empty")
                
            # Validate vote value
            if vote not in [0, 1]:
                raise HTTPException(status_code=400, detail=f"Invalid vote value for {exp_id}. Must be 0 or 1.")
            
            # Check if experiment record exists
            key = {'id': exp_id}
            item = experiment_db.read(key)
            
            if item:
                # Record exists, update the score
                current_score = item.get("scores", 0)
                new_score = current_score + vote
                
                # Prepare data for update
                update_data = {"scores": new_score}
                
                try:
                    success = experiment_db.update(
                        key=key,
                        data=update_data
                    )
                    if not success:
                        logger.error(f"Failed to update score for {exp_id}")
                        raise HTTPException(status_code=500, detail=f"Database update failed for {exp_id}")
                except Exception as e:
                    logger.error(f"Failed to update score for {exp_id}: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Database update failed for {exp_id}")
                
                results[exp_id] = {"previous_score": current_score, "new_score": new_score}
                logger.info(f"Updated score for {exp_id}: {current_score} -> {new_score}")
            
            else:
                # Record doesn't exist
                logger.warning(f"Cannot find experiment: {exp_id}")
                raise HTTPException(status_code=404, detail=f"Experiment {exp_id} not found")

        return {
            "status": "success",
            "message": "Votes recorded successfully",
            "results": results
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error recording votes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to record votes: {str(e)}")