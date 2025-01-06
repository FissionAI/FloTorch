from config.config import get_config
from config.experimental_config import ExperimentalConfig
import logging
from baseclasses.base_classes import BaseInferencer
from typing import Dict, Type

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class InferenceServiceError(Exception):
    """Custom exception for inference service related errors"""
    pass


class InferencerFactory:

    """Factory to create embedders based on model ID and service type."""

    _registry: Dict[str, Type[BaseInferencer]] = {}

    @classmethod
    def register_inferencer(cls, service_type: str, model_id: str, embedder_cls: Type[BaseInferencer]):
        key = f"{service_type}:{model_id}"
        cls._registry[key] = embedder_cls
    
    @classmethod
    def create_inferencer(cls, experimentalConfig : ExperimentalConfig) -> BaseInferencer:
        service_type = experimentalConfig.retrieval_service
        model_id = experimentalConfig.retrieval_model
        key = f"{service_type}:{model_id}"

        inferencer_cls = cls._registry.get(key)
        if not inferencer_cls:
            raise InferenceServiceError(f"No inferencer_cls registered for service {service_type} and model {model_id}")
        
        if service_type == "sagemaker":
            role_arn = get_config().sagemaker_role_arn
        elif service_type == "bedrock":
            role_arn = get_config().bedrock_role_arn
        else:
            role_arn = None
        
        # return inferencer_cls(model_id=model_id, region=experimentalConfig.aws_region, experiment_config=experimentalConfig)
        return inferencer_cls(
            model_id=model_id,
            experiment_config=experimentalConfig,
            region=experimentalConfig.aws_region,
            role_arn=role_arn
        )