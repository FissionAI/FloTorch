import logging
from typing import Type, Dict

from baseclasses.base_classes import BaseEmbedder
from config.config import get_config
from config.experimental_config import ExperimentalConfig

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class EmbedderFactory:
    """Factory to create embedders based on model ID and service type."""

    _registry: Dict[str, Type[BaseEmbedder]] = {}

    @classmethod
    def register_embedder(cls, service_type: str, model_id: str, embedder_cls: Type[BaseEmbedder]):
        key = f"{service_type}:{model_id}"
        cls._registry[key] = embedder_cls

    @classmethod
    def create_embedder(cls, experimentalConfig : ExperimentalConfig) -> BaseEmbedder:
        service_type = experimentalConfig.embedding_service
        model_id = experimentalConfig.embedding_model
        key = f"{service_type}:{model_id}"

        if experimentalConfig.embedding_service == "sagemaker":
            role_arn = get_config().sagemaker_role_arn
        elif experimentalConfig.embedding_service == "bedrock":
            role_arn = get_config().bedrock_role_arn
        embedder_cls = cls._registry.get(key)
        if not embedder_cls:
            raise ValueError(f"No embedder registered for service {service_type} and model {model_id}")
        
        return embedder_cls(model_id, experimentalConfig.aws_region, role_arn)

