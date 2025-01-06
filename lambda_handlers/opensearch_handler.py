import json
import logging
from typing import Dict, Any

from config.config import Config
from opensearch.opensearch_index_manager import OpenSearchIndexManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler to create OpenSearch indices based on experiment configurations.
    
    Args:
        event (Dict[str, Any]): Lambda event containing experiment configurations
        context (Any): Lambda context object
    
    Returns:
        Dict[str, Any]: Response containing execution status and details
    """
    try:
        logger.info("Processing event: %s", json.dumps(event))

        # Initialize handler with configuration
        config = Config.load_config()
        opensearch_indexer = OpenSearchIndexManager(config)

        # Create indices
        opensearch_indexer.create_indices(event)

        return {"status": "success"}

    except Exception as e:
        logger.error("Error processing event: %s", str(e))
        return {
            "status": "failed",
            "errorMessage": str(e)
        }
