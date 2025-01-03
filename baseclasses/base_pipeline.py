import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from config import Config, ExperimentalConfig
from core.dynamodb import DynamoDBOperations
from core.opensearch_vectorstore import OpenSearchVectorDatabase

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class BasePipeline(ABC):
    def __init__(self, config: Config, experimentalConfig: ExperimentalConfig):
        """
        Base class for common functionality in both Indexer and Retriever classes.

        Args:
            config (Config): Global configuration object
            experimentalConfig (ExperimentalConfig): Experiment-specific configuration
        """
        self.config = config
        self.experimentalConfig = experimentalConfig
        self.components = self.initialize_components()

    def initialize_components(self) -> Dict[str, Any]:
        """Initialize all required components for the pipeline."""
        try:
            logger.info("Initializing common components")

            # Initialize DynamoDB and OpenSearch connections
            metrics_dynamodb = DynamoDBOperations(region=self.config.aws_region,
                                                  table_name=self.config.experiment_question_metrics_table)
            experiment_dynamodb = DynamoDBOperations(region=self.config.aws_region,
                                                     table_name=self.config.experiment_table)

            vector_database = OpenSearchVectorDatabase(
                host=self.config.opensearch_host,
                is_serverless=self.config.opensearch_serverless,
                region=self.config.aws_region,
                username=self.config.opensearch_username,
                password=self.config.opensearch_password
            )

            return {
                "vector_database": vector_database,
                "metrics_dynamodb": metrics_dynamodb,
                "experiment_dynamodb": experiment_dynamodb
            }
        except Exception as e:
            logger.error(f"Failed to initialize components: {str(e)}")
            raise

    def log_dynamodb_update(self, retrieval_query_embed_tokens: int, retrieval_input_tokens: int,
                            retrieval_output_tokens: int) -> None:
        """Log and update DynamoDB with token usage."""
        try:
            self.components['experiment_dynamodb'].update_item(
                key={"id": self.experimentalConfig.experiment_id},
                update_expression="SET retrieval_query_embed_tokens = :rqembed, retrieval_input_tokens = :rinput, retrieval_output_tokens = :routput",
                expression_values={
                    ":rqembed": retrieval_query_embed_tokens,
                    ":rinput": retrieval_input_tokens,
                    ":routput": retrieval_output_tokens,
                },
            )
        except Exception as e:
            logger.error(f"Failed to update DynamoDB: {str(e)}")

    @abstractmethod
    def execute(self) -> None:
        """Abstract method for subclasses to implement their specific pipeline logic."""
        pass
