import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration class for AWS and OpenSearch settings."""
    profile_name: Optional[str]
    aws_region: str
    bedrock_endpoint_url: Optional[str]
    opensearch_host: str
    vector_field: str
    vector_index_name: str
    opensearch_serverless: bool
    execution_table: str
    experiment_table: str
    experiment_question_metrics_table: str
    experiment_question_metrics_experimentid_index: str
    execution_model_invocations_table: str
    opensearch_username: Optional[str]
    opensearch_password: Optional[str]
    step_function_arn : str
    inference_system_prompt : str
    s3_bucket : str
    bedrock_role_arn : str
    sagemaker_role_arn: str
    bedrock_limit_csv_path: str

    @staticmethod
    def load_config() -> 'Config':
        """
        Load configuration from environment variables.
        
        Returns:
            Config: Configuration object with loaded values
        """
        load_dotenv()
        
        return Config(
            profile_name=os.getenv('profile_name'),
            aws_region=os.getenv('aws_region', 'us-east-1'),
            bedrock_endpoint_url=os.getenv('bedrock_endpoint_url'),
            opensearch_host=os.getenv('opensearch_host', ''),
            vector_field=os.getenv('vector_field_name', 'vectors'),
            vector_index_name=os.getenv('vector_index_name', ''),
            opensearch_serverless=os.getenv('opensearch_serverless', 'false').lower() == 'true',
            execution_table=os.getenv('execution_table', ''),
            experiment_table=os.getenv('experiment_table', ''),
            experiment_question_metrics_table=os.getenv('experiment_question_metrics_table', ''),
            experiment_question_metrics_experimentid_index = os.getenv('experiment_question_metrics_experimentid_index', ''),
            execution_model_invocations_table=os.getenv('execution_model_invocations_table', ''),
            opensearch_password=os.getenv('opensearch_password', ''),
            opensearch_username=os.getenv('opensearch_username', ''),
            step_function_arn=os.getenv('step_function_arn', ''),
            inference_system_prompt=os.getenv('inference_system_prompt', ''),
            s3_bucket=os.getenv('s3_bucket', ''),
            bedrock_role_arn=os.getenv('bedrock_role_arn', ''),
            sagemaker_role_arn=os.getenv('sagemaker_role_arn', ''),
            bedrock_limit_csv_path=os.getenv('bedrock_limit_csv', '')
            )


def get_config() -> Config:
    """
    Get validated configuration.
    
    Returns:
        Config: Validated configuration object
        
    Raises:
        ValueError: If configuration validation fails
    """
    config = Config.load_config()
    return config
