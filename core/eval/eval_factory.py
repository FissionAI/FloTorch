import logging
from typing import Dict, Type

from baseclasses.base_classes import BaseEvaluator
from config.config import Config
from config.experimental_config import ExperimentalConfig

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class EvaluatorServiceError(Exception):
    """Custom exception for inference service related errors"""
    pass

class EvalFactory:

    _registry: Dict[str, Type[BaseEvaluator]] = {}

    @classmethod
    def register_evaluator(cls, service_type: str, eval_type: str, evaluator_cls: Type[BaseEvaluator]):
        key = f"{service_type}:{eval_type}"
        cls._registry[key] = evaluator_cls

    @classmethod
    def create_evaluator(cls, experimentalConfig: ExperimentalConfig) -> BaseEvaluator:
        config = Config.load_config()
        
        eval_service_type = experimentalConfig.eval_service
        eval_type = 'llm' if experimentalConfig.llm_based_eval else 'non_llm' 

        key = f"{eval_service_type}:{eval_type}"

        evaluator_cls = cls._registry.get(key)
        if not evaluator_cls:
            raise EvaluatorServiceError(f"No evaluator_cls registered for service {eval_service_type} and type {eval_type}")
        
        return evaluator_cls(config=config, experimental_config=experimentalConfig)
