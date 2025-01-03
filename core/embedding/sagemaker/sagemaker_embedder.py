import logging
import re
from typing import Dict, List

import boto3
from sagemaker import get_execution_role
from sagemaker.deserializers import JSONDeserializer
from sagemaker.huggingface import HuggingFaceModel
from sagemaker.predictor import Predictor
from sagemaker.serializers import JSONSerializer
from sagemaker.session import Session

from baseclasses.base_classes import BaseEmbedder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Sagemaker Base Embedder
class SageMakerEmbedder(BaseEmbedder):
    def __init__(self, model_id: str, region: str, role_arn: str) -> None:
        super().__init__(model_id)
        self.client = boto3.client("sagemaker-runtime", region_name=region)
        self.sagemaker_client = boto3.client('sagemaker', region_name=region)
        self.endpoint_name = self._sanitize_name(self.model_id)
        self.role_arn = role_arn
        self.session = Session(boto_session=boto3.Session(region_name=region))
        self._ensure_endpoint_exists()
        self.predictor = Predictor(
            endpoint_name=self.endpoint_name,
            sagemaker_session=self.session
        )
        self.predictor.serializer = JSONSerializer()
        self.predictor.deserializer = JSONDeserializer()
        

    def _ensure_endpoint_exists(self):
        """Create endpoint if it doesn't exist"""
        try:
            self.sagemaker_client.describe_endpoint(EndpointName=self.endpoint_name)
            logger.info(f"Endpoint {self.endpoint_name} already exists")
        except self.sagemaker_client.exceptions.ClientError:
            logger.info(f"Creating endpoint {self.endpoint_name}")
            self._create_endpoint()

    def _create_endpoint(self):
        """Create a new SageMaker endpoint for the BGE model"""
        
        # TODO: move this based on config endpoint
        instance_type = "ml.g5.2xlarge"
        
        # Create unique names for model and config
        model_name = f"{self.endpoint_name}-model"
        config_name = f"{self.endpoint_name}-config"
        
        # HF model configuration
        hub = {
            'HF_MODEL_ID': self.model_id,
            'HF_TASK': 'feature-extraction'
        }
        
        # Create HuggingFace Model
        huggingface_model = HuggingFaceModel(
            env=hub,
            role=self._get_role(),
            transformers_version="4.26.0",
            pytorch_version="1.13.1",
            py_version="py39",
            sagemaker_session=self.session
        )
        
        # Deploy the model
        huggingface_model.deploy(
            initial_instance_count=1,
            instance_type=instance_type,
            endpoint_name=self.endpoint_name,
            endpoint_config_name=config_name
        )
        
        logger.info(f"Endpoint {self.endpoint_name} created successfully")

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """
        Sanitize the name to follow AWS naming conventions
        - Must be between 1 and 63 characters long
        - Must consist of alphanumeric characters and/or hyphens
        - Must not contain spaces or special characters
        """
        # Replace invalid characters with hyphens
        sanitized = re.sub(r'[^a-zA-Z0-9-]', '-', name)
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        # Ensure length constraints
        if len(sanitized) > 63:
            sanitized = sanitized[:63]
        return sanitized

    def prepare_payload(self, text: str, dimensions: int, normalize: bool) -> Dict:
        raise NotImplementedError("Subclasses must implement `prepare_payload`")

    def embed(self, text: str, dimensions: int = 256, normalize: bool = True) -> List[float]:
        raise NotImplementedError("Subclasses must implement `embed`")

    def extract_embedding(self, response: Dict) -> List[float]:
        raise NotImplementedError("Subclasses must implement `extract_embedding`")
    
    def _get_role(self):
        """Get current SageMaker execution role with fallback"""
        try:
            role = get_execution_role()
            logger.info(f"Using execution role: {role}")
            return role
        except ValueError as e:
            # Fallback to checking if running with IAM role
            try:
                sts = boto3.client('sts')
                caller_identity = sts.get_caller_identity()
                role_arn = caller_identity['Arn']
                if ':assumed-role/' in role_arn:
                    # Extract the role ARN from the assumed role
                    role_arn = role_arn.replace(':assumed-role/', ':role/').rsplit('/', 1)[0]
                    logger.info(f"Using IAM role: {role_arn}")
                    return role_arn
            except Exception as sts_error:
                logger.error(f"Failed to get role from STS: {sts_error}")
            
            logger.error("Failed to get execution role. Make sure you're running in a SageMaker context or provide a role ARN.")
            return self.role_arn
