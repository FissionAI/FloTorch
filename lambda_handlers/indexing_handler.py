import json
import logging
from typing import Dict, Any

from config.config import Config
from config.experimental_config import ExperimentalConfig
from indexing.indexing import Indexer

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler to invoke the retrieve method.
    
    Args:
        event (Dict[str, Any]): Lambda event containing configuration parameters
        context (Any): Lambda context object
    
    Returns:
        Dict[str, Any]: Response containing execution status and details
    """
    try:
        # Validate input parameters

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
            indexing_algorithm=exp_config_data.get('indexing_algorithm')
        )
        logger.info("Processing event: %s", json.dumps(event))

        # Load base configuration
        config = Config.load_config()
           
        # Execute retrieve method
        Indexer().chunk_embed_store(config, exp_config)

        return {
            **event,  # Pass the entire input event
            "status": "success"
        }
    except Exception as e:
        logger.error("Error processing event: %s", str(e))
        return {
            **event,  # Pass the entire input event
            "status": "failed",
            "errorMessage": str(e)
        }

