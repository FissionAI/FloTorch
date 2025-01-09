import logging
from typing import Type, Dict

from baseclasses.base_classes import BaseEmbedder

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class EmbedderFactory:
    """Factory to create embedders based on model ID and service type."""

    _registry: Dict[str, Type[BaseEmbedder]] = {}

    @classmethod
    def register_embedder(cls, service_type: str, model_id: str, embedder_cls: Type[BaseEmbedder]):
        """
        Registers an embedder class for a given service type and model ID.

        Args:
            service_type (str): The type of embedding service (e.g., "sagemaker", "bedrock").
            model_id (str): The ID of the embedding model.
            embedder_cls (Type[BaseEmbedder]): The embedder class to register.
        """
        key = f"{service_type}:{model_id}"
        cls._registry[key] = embedder_cls

    @classmethod
    def create_embedder(
        cls,
        service_type: str,
        model_id: str,
        aws_region: str,
        role_arn: str
    ) -> BaseEmbedder:
        """
        Creates an embedder instance based on the given parameters.

        Args:
            service_type (str): The type of embedding service (e.g., "sagemaker", "bedrock").
            model_id (str): The ID of the embedding model.
            aws_region (str): The AWS region where the service is hosted.
            role_arn (str): The AWS role ARN for authentication.

        Returns:
            BaseEmbedder: An instance of the appropriate embedder class.

        Raises:
            ValueError: If no embedder is registered for the given service type and model ID.
        """
        key = f"{service_type}:{model_id}"
        embedder_cls = cls._registry.get(key)
        if not embedder_cls:
            raise ValueError(f"No embedder registered for service {service_type} and model {model_id}")

        return embedder_cls(model_id, aws_region, role_arn)