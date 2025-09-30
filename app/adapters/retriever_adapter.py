"""
Retriever service adapter with feature flag to switch between local and external service.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from app.adapters.http_service_adapter import HTTPServiceAdapter, ServiceConfig

logger = logging.getLogger(__name__)

class RetrieverAdapter:
    """
    Adapter that can use either local retriever implementation or external HTTP service.
    Controlled by USE_EXTERNAL_SERVICES environment variable.
    """
    
    def __init__(self, config: Dict[str, Any], experimental_config: Dict[str, Any]):
        self.use_external = os.getenv("USE_EXTERNAL_SERVICES", "false").lower() == "true"
        
        if self.use_external:
            logger.info("Using external retriever service")
            self._init_external_service()
        else:
            logger.info("Using local retriever implementation")
            self._init_local()
    
    def _init_external_service(self):
        """Initialize external retriever service."""
        retriever_url = os.getenv("RETRIEVER_SERVICE_URL", "http://localhost:8001")
        service_config = ServiceConfig(
            base_url=retriever_url,
            timeout=int(os.getenv("RETRIEVER_TIMEOUT", "60")),
            max_retries=int(os.getenv("RETRIEVER_MAX_RETRIES", "3"))
        )
        self.client = HTTPServiceAdapter(service_config)
    
    def _init_local(self):
        """Initialize local retriever implementation."""
        # Import local retriever function
        from retriever.retriever import retrieve
        self.retrieve_func = retrieve
    
    def retrieve(self, config: Any, experimental_config: Any) -> None:
        """
        Execute retrieval process.
        
        Args:
            config: Global configuration object
            experimental_config: Experiment-specific configuration
        """
        if self.use_external:
            return self._retrieve_external(config, experimental_config)
        else:
            return self._retrieve_local(config, experimental_config)
    
    def _retrieve_external(self, config: Any, experimental_config: Any) -> None:
        """Execute retrieval using external service."""
        try:
            # Convert config objects to dictionaries for JSON serialization
            config_dict = self._config_to_dict(config)
            experimental_config_dict = self._config_to_dict(experimental_config)
            
            payload = {
                "config": config_dict,
                "experimental_config": experimental_config_dict
            }
            
            response = self.client.post("/retrieve", json=payload)
            logger.info(f"External retriever response: {response}")
            
        except Exception as e:
            logger.error(f"External retriever failed: {e}")
            raise
    
    def _retrieve_local(self, config: Any, experimental_config: Any) -> None:
        """Execute retrieval using local implementation."""
        return self.retrieve_func(config, experimental_config)
    
    def _config_to_dict(self, config_obj: Any) -> Dict[str, Any]:
        """Convert config object to dictionary for JSON serialization."""
        if hasattr(config_obj, '__dict__'):
            return {k: v for k, v in config_obj.__dict__.items() 
                   if not k.startswith('_')}
        return config_obj
