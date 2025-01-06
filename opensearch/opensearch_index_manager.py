import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from config.config import Config
from core.opensearch_vectorstore import OpenSearchVectorDatabase
from util.dynamo_utils import deserialize_dynamodb_json

logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


@dataclass
class OpenSearchIndex:
    """
    Data class representing the configuration for an OpenSearch index.
    
    Attributes:
        name (str): Unique identifier for the index
        algorithm (str): Indexing algorithm to be used
        vector_field (str): Name of the vector field
        dimension (int): Dimensionality of the vector
    """
    name: str
    algorithm: str
    vector_field: str
    dimension: int


class OpenSearchIndexManager:
    """
    Manager class for handling OpenSearch index operations.
    
    Responsible for initializing OpenSearch connections and creating indices.
    """

    def __init__(self, config: Config):
        """
        Initialize the OpenSearch index manager.
        
        Args:
            config (Config): Configuration object with OpenSearch connection details
        """
        self.config = config
        self.opensearch_db = self._initialize_opensearch()

    def _initialize_opensearch(self) -> OpenSearchVectorDatabase:
        """
        Initialize and return an OpenSearch vector database connection.
        
        Returns:
            OpenSearchVectorDatabase: Configured OpenSearch database connection
        
        Raises:
            Exception: If connection initialization fails
        """
        try:
            return OpenSearchVectorDatabase(
                host=self.config.opensearch_host,
                is_serverless=self.config.opensearch_serverless,
                region=self.config.aws_region,
                username=self.config.opensearch_username,
                password=self.config.opensearch_password
            )
        except Exception as e:
            logger.error(f"Failed to initialize OpenSearch connection: {e}")
            raise

    def _create_index_mapping(self, index: OpenSearchIndex) -> Dict[str, Any]:
        """
        Generate the mapping configuration for an OpenSearch index.
        
        Args:
            index (OpenSearchIndex): Index configuration details
        
        Returns:
            Dict[str, Any]: Mapping configuration for the index
        """
        return {
            "properties": {
                index.vector_field: {
                    "type": "knn_vector",
                    "dimension": index.dimension
                },
                "text": {
                    "type": "text"
                }
            }
        }

    def _validate_experiment_config(self, config_data: Dict[str, Any]) -> Optional[OpenSearchIndex]:
        """
        Validate and extract OpenSearch index configuration from experiment config.
        
        Args:
            config_data (Dict[str, Any]): Raw configuration dictionary
        
        Returns:
            Optional[OpenSearchIndex]: Validated index configuration or None
        """
        try:
            # Validate required configuration fields
            index_id = config_data.get('index_id')
            config = config_data.get('config', {})

            if not index_id or not config:
                logger.warning(f"Invalid configuration: Missing index_id or config - {config_data}")
                return None

            # Extract configuration details
            return OpenSearchIndex(
                name=index_id,
                algorithm=config.get('indexing_algorithm', ''),
                vector_field=self.config.vector_field,
                dimension=config.get('vector_dimension', 0)
            )
        except Exception as e:
            logger.error(f"Error processing experiment configuration: {e}")
            return None

    def create_indices(self, experiment_configs: List[Dict[str, Any]]) -> None:
        """
        Create OpenSearch indices based on experiment configurations.
        
        Args:
            experiment_configs (List[Dict[str, Any]]): List of experiment configurations
        """
        processed_index_ids = set()

        for raw_config in experiment_configs:
            # Deserialize configuration
            try:
                config_data = deserialize_dynamodb_json(raw_config)
            except Exception as e:
                logger.error(f"Failed to deserialize configuration: {e}")
                continue

            # Validate and extract index configuration
            index_config = self._validate_experiment_config(config_data)
            # continuing incase of any index creation fails for a certain experiment
            # so that rest of the experiments can continue
            if not index_config:
                continue

            # Skip if index already processed
            if index_config.name in processed_index_ids:
                logger.info(f"Skipping duplicate index: {index_config.name}")
                continue

            # Check if index already exists
            if self.opensearch_db.index_exists(index_name=index_config.name):
                logger.info(f"Index {index_config.name} already exists")
                processed_index_ids.add(index_config.name)
                continue

            try:
                # Generate mapping and create index
                mapping = self._create_index_mapping(index_config)
                self.opensearch_db.create_index(
                    index_name=index_config.name,
                    algorithm=index_config.algorithm,
                    mapping=mapping
                )
                processed_index_ids.add(index_config.name)
                logger.info(f"Successfully created index: {index_config.name}")

            except Exception as e:
                logger.error(f"Failed to create index {index_config.name}: {e}")
