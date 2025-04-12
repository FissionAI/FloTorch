import json
from typing import Dict, Any
from config.config import Config
from config.experimental_config import ExperimentalConfig
from evaluation.eval import evaluate
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler to invoke the eval method.
    
    Args:
        event (Dict[str, Any]): Lambda event containing configuration parameters
        context (Any): Lambda context object
    
    Returns:
        Dict[str, Any]: Response containing status and message
    """
    try:

        # Extract experimental configuration from event
        logger.info("Processing event: %s", json.dumps(event))
        exp_config_data = event
        exp_config = ExperimentalConfig(
            execution_id=exp_config_data.get('execution_id'),
            experiment_id=exp_config_data.get('experiment_id'),
            embedding_model=exp_config_data.get('embedding_model'),
            retrieval_model=exp_config_data.get('retrieval_model'),
            vector_dimension=exp_config_data.get('vector_dimension'),
            gt_data=exp_config_data.get('gt_data'),
            index_id=exp_config_data.get('index_id'),
            knn_num=exp_config_data.get('knn_num'),
            temp_retrieval_llm=exp_config_data.get('temp_retrieval_llm'),
            embedding_service=exp_config_data.get('embedding_service'),
            retrieval_service=exp_config_data.get('retrieval_service'),
            aws_region=exp_config_data.get('aws_region'),
            chunking_strategy=exp_config_data.get('chunking_strategy'),
            chunk_size=exp_config_data.get('chunk_size'),
            chunk_overlap=exp_config_data.get('chunk_overlap'),
            hierarchical_parent_chunk_size=exp_config_data.get('hierarchical_parent_chunk_size'),
            hierarchical_child_chunk_size=exp_config_data.get('hierarchical_child_chunk_size'),
            hierarchical_chunk_overlap_percentage=exp_config_data.get('hierarchical_chunk_overlap_percentage'),
            kb_data=exp_config_data.get('kb_data'),
            n_shot_prompts=exp_config_data.get('n_shot_prompts'),
            n_shot_prompt_guide=exp_config_data.get('n_shot_prompt_guide'),
            indexing_algorithm=exp_config_data.get('indexing_algorithm'),
            bedrock_knowledge_base=exp_config_data.get('bedrock_knowledge_base', False),
            knowledge_base=exp_config_data.get('knowledge_base', False),
            eval_service=exp_config_data.get('eval_service', "ragas"), 
            eval_embedding_model=exp_config_data.get('eval_embedding_model', "amazon.titan-embed-text-v1"), #amazon.nova-pro-v1:0
            eval_retrieval_model=exp_config_data.get('eval_retrieval_model', "mistral.mixtral-8x7b-instruct-v0:1"),
        )
        logger.info("Processing event: %s", json.dumps(event))


        evaluate(exp_config)

        return {
            "status": "success"
        }
    except Exception as e:
        logger.error("Error in lambda_handler: %s", str(e))
        return {
            "status": "failed",
            "errorMessage": str(e)
        }

