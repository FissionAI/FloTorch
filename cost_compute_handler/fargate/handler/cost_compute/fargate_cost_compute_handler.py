import os
import json
from fargate.cost_compute_processor import RetrieverProcessor
from flotorch_core.logger.global_logger import get_logger
from flotorch_core.config.config import Config
from flotorch_core.config.env_config_provider import EnvConfigProvider

logger = get_logger()

# Initialize configuration provider and config
env_config_provider = EnvConfigProvider()
config = Config(env_config_provider)


def get_environment_data():
    """
    Fetches task token and input data from environment variables.
    Returns:
        tuple: Task token (str) and input data (dict).
    """
    input_data = {"experiment_id":os.getenv("experiment_id")}
    return input_data


def main():
    """
    Main entry point for the Fargate retriever handler.
    """
    try:
        input_data = get_environment_data()

        # Initialize and process the RetrieverProcessor
        fargate_processor = RetrieverProcessor(input_data)
        fargate_processor.process()
    except Exception as e:
        logger.error(f"Error processing experiment cost calculation: {str(e)}")
        raise


if __name__ == "__main__":
    main()