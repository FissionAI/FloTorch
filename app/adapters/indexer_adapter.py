"""
Indexer service adapter with feature flag to switch between local and external service.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from app.adapters.http_service_adapter import HTTPServiceAdapter, ServiceConfig

logger = logging.getLogger(__name__)

class IndexerAdapter:
    """
    Adapter that can use either local indexer implementation or external HTTP service.
    Controlled by USE_EXTERNAL_SERVICES environment variable.
    """
    
    def __init__(self, config: Dict[str, Any], experimental_config: Dict[str, Any]):
        self.use_external = os.getenv("USE_EXTERNAL_SERVICES", "false").lower() == "true"
        
        if self.use_external:
            logger.info("Using external indexer service")
            self._init_external_service()
        else:
            logger.info("Using local indexer implementation")
            self._init_local()
    
    def _init_external_service(self):
        """Initialize external indexer service."""
        indexer_url = os.getenv("INDEXER_SERVICE_URL", "http://localhost:8002")
        service_config = ServiceConfig(
            base_url=indexer_url,
            timeout=int(os.getenv("INDEXER_TIMEOUT", "300")),  # Longer timeout for indexing
            max_retries=int(os.getenv("INDEXER_MAX_RETRIES", "2"))
        )
        self.client = HTTPServiceAdapter(service_config)
    
    def _init_local(self):
        """Initialize local indexer implementation."""
        from indexing.indexing import chunk_embed_store
        self.chunk_embed_store_func = chunk_embed_store
    
    def chunk_embed_store(self, config: Any, experimental_config: Any) -> None:
        """
        Execute chunking, embedding, and storage process.
        
        Args:
            config: Global configuration object
            experimental_config: Experiment-specific configuration
        """
        if self.use_external:
            return self._index_external(config, experimental_config)
        else:
            return self._index_local(config, experimental_config)
    
    def _index_external(self, config: Any, experimental_config: Any) -> None:
        """Execute indexing using external service."""
        try:
            # Convert config objects to dictionaries for JSON serialization
            config_dict = self._config_to_dict(config)
            experimental_config_dict = self._config_to_dict(experimental_config)
            
            payload = {
                "config": config_dict,
                "experimental_config": experimental_config_dict
            }
            
            response = self.client.post("/index", json=payload)
            logger.info(f"External indexer response: {response}")
            
        except Exception as e:
            logger.error(f"External indexer failed: {e}")
            raise
    
    def _index_local(self, config: Any, experimental_config: Any) -> None:
        """Execute indexing using local implementation."""
        return self.chunk_embed_store_func(config, experimental_config)
    
    def _config_to_dict(self, config_obj: Any) -> Dict[str, Any]:
        """Convert config object to dictionary for JSON serialization."""
        if hasattr(config_obj, '__dict__'):
            return {k: v for k, v in config_obj.__dict__.items() 
                   if not k.startswith('_')}
        return config_obj
