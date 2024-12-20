import json
from typing import Dict, Any
from retriever.retriever import retrieve
from config.config import Config
from config.experimental_config import ExperimentalConfig
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
            kb_data=exp_config_data.get('kb_data'),
            n_shot_prompts=exp_config_data.get('n_shot_prompts'),
            n_shot_prompt_guide=exp_config_data.get('n_shot_prompt_guide'),
            n_shot_prompt_guide_obj=exp_config_data.get('n_shot_prompt_guide_obj'),
            indexing_algorithm=exp_config_data.get('indexing_algorithm')
        )

        # Load base configuration
        config = Config.load_config()
        
        # Execute retrieve method
        retrieve(config, exp_config)

        return {
            "status": "success",
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Retrieval process completed successfully',
                'executionId': exp_config.execution_id,
                'experimentId': exp_config.experiment_id
            })
        }

    except ValueError as ve:
        logger.error("Validation Error: %s", str(ve))
        return {
            "status": "failed",
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Validation Error',
                'message': str(ve)
            })
        }
    except Exception as e:
        logger.error("Internal Server Error: %s", str(e))
        return {
            "status": "failed",
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e)
            })
        }
