"""
Evaluation service adapter with feature flag to switch between local and external service.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from app.adapters.http_service_adapter import HTTPServiceAdapter, ServiceConfig

logger = logging.getLogger(__name__)

class EvalAdapter:
    """
    Adapter that can use either local evaluation implementation or external HTTP service.
    Controlled by USE_EXTERNAL_SERVICES environment variable.
    """
    
    def __init__(self, config: Dict[str, Any], experimental_config: Dict[str, Any]):
        self.use_external = os.getenv("USE_EXTERNAL_SERVICES", "false").lower() == "true"
        
        if self.use_external:
            logger.info("Using external evaluation service")
            self._init_external_service()
        else:
            logger.info("Using local evaluation implementation")
            self._init_local()
    
    def _init_external_service(self):
        """Initialize external evaluation service."""
        eval_url = os.getenv("EVAL_SERVICE_URL", "http://localhost:8003")
        service_config = ServiceConfig(
            base_url=eval_url,
            timeout=int(os.getenv("EVAL_TIMEOUT", "120")),
            max_retries=int(os.getenv("EVAL_MAX_RETRIES", "2"))
        )
        self.client = HTTPServiceAdapter(service_config)
    
    def _init_local(self):
        """Initialize local evaluation implementation."""
        from evaluation.eval import evaluate
        self.evaluate_func = evaluate
    
    def evaluate(self, config: Any, experimental_config: Any) -> None:
        """
        Execute evaluation process.
        
        Args:
            config: Global configuration object
            experimental_config: Experiment-specific configuration
        """
        if self.use_external:
            return self._evaluate_external(config, experimental_config)
        else:
            return self._evaluate_local(config, experimental_config)
    
    def _evaluate_external(self, config: Any, experimental_config: Any) -> None:
        """Execute evaluation using external service."""
        try:
            # Convert config objects to dictionaries for JSON serialization
            config_dict = self._config_to_dict(config)
            experimental_config_dict = self._config_to_dict(experimental_config)
            
            payload = {
                "config": config_dict,
                "experimental_config": experimental_config_dict
            }
            
            response = self.client.post("/evaluate", json=payload)
            logger.info(f"External evaluator response: {response}")
            
        except Exception as e:
            logger.error(f"External evaluator failed: {e}")
            raise
    
    def _evaluate_local(self, config: Any, experimental_config: Any) -> None:
        """Execute evaluation using local implementation."""
        return self.evaluate_func(config, experimental_config)
    
    def _config_to_dict(self, config_obj: Any) -> Dict[str, Any]:
        """Convert config object to dictionary for JSON serialization."""
        if hasattr(config_obj, '__dict__'):
            return {k: v for k, v in config_obj.__dict__.items() 
                   if not k.startswith('_')}
        return config_obj
