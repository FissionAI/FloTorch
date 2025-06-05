from baseclasses.base_classes import BaseEvaluator
from config.experimental_config import ExperimentalConfig
from config.config import Config
from typing import Dict, Type

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class EvaluatorServiceError(Exception):
    """Custom exception for inference service related errors"""
    pass

class EvalFactory:

    _registry: Dict[str, Type[BaseEvaluator]] = {}

    @classmethod
    def register_evaluator(cls, service_type: str, llm_service: str, evaluator_cls: Type[BaseEvaluator]):
        key = f"{service_type}:{llm_service}"
        cls._registry[key] = evaluator_cls

    @classmethod
    def create_evaluator(cls, experimentalConfig: ExperimentalConfig) -> BaseEvaluator:
        config = Config.load_config()
        
        eval_service = experimentalConfig.eval_service
        llm_service = 'custom_gateway' if experimentalConfig.gateway_enabled else 'bedrock'
        
        key = f"{eval_service}:{llm_service}"

        evaluator_cls = cls._registry.get(key)
        if not evaluator_cls:
            raise EvaluatorServiceError(f"No evaluator_cls registered for service {eval_service_type} and type {llm_service}")
        
        return evaluator_cls(config=config, experimental_config=experimentalConfig)
