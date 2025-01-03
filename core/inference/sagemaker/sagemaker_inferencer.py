import logging
from abc import abstractmethod
from typing import List, Dict

import boto3

from baseclasses.base_classes import BaseInferencer

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class SageMakerInferencer(BaseInferencer):
    """Base class for SageMaker models - each model needs its own implementation"""

    @abstractmethod
    def _get_endpoint_name(self) -> str:
        """Each SageMaker model implementation should provide its endpoint name"""
        pass

    def _initialize_client(self) -> None:
        self.client = boto3.client(
            service_name='sagemaker-runtime',
            region_name=self.region
        )
        self.endpoint_name = self._get_endpoint_name()

    def generate_text(self, user_query: str, context: List[Dict], default_prompt: str, **kwargs) -> str:
        raise NotImplementedError("Subclasses must implement `extract_embedding`")
