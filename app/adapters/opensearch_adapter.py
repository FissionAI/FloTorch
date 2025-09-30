"""
OpenSearch adapter backed by opensearch-py (no dependency on local `core`).
This avoids any 'core' imports and works with Docker OpenSearch out-of-the-box.
"""
import logging
from typing import Dict, Any, List, Optional
from opensearchpy import OpenSearch, RequestsHttpConnection

logger = logging.getLogger(__name__)

class OpenSearchAdapter:
    """
    Adapter that uses opensearch-py client under the hood.
    """

    def __init__(self, host: str, use_ssl: bool = False, port: int = 9200,
                 is_serverless: bool = False, region: str = 'us-east-1',
                 username: str = None, password: str = None):

        # For local/dev Docker OpenSearch, defaults are: http on port 9200, no auth
        http_auth = (username, password) if (username and password) else None
        verify_certs = True if use_ssl else False

        self.client = OpenSearch(
            hosts=[{"host": host, "port": port}],
            http_auth=http_auth,
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            connection_class=RequestsHttpConnection,
            timeout=30,
            max_retries=3,
            retry_on_timeout=True,
        )
    
    # ---------------- Convenience methods ----------------
    
    # Delegate all methods to the underlying client
    def create_index(self, index_name: str, mapping: Dict[str, Any], algorithm: str) -> None:
        return self.client.create_index(index_name, mapping, algorithm)
    
    def update_index(self, index_name: str, new_mapping: Dict[str, Any]) -> None:
        return self.client.update_index(index_name, new_mapping)
    
    def delete_index(self, index_name: str) -> None:
        return self.client.delete_index(index_name)
    
    def insert_document(self, index_name: str, document: Dict[str, Any]) -> None:
        return self.client.insert_document(index_name, document)
    
    def search(self, index_name: str, query_vector: List[float], k: int) -> List[Dict[str, Any]]:
        return self.client.search(index_name, query_vector, k)
    
    def index_exists(self, index_name: str) -> bool:
        return self.client.index_exists(index_name)
    
    def insert_chunk(self, index_name: str, text: str, embedding: List[float], 
                    chunk_id: str, metadata: Dict = None):
        return self.client.insert_chunk(index_name, text, embedding, chunk_id, metadata)
    
    def batch_insert_chunks(self, index_name: str, chunks: List[str], 
                           chunk_embeddings: List[List[float]], 
                           metadata: Optional[List[Dict]] = None, 
                           batch_size: int = 100):
        return self.client.batch_insert_chunks(
            index_name, chunks, chunk_embeddings, metadata, batch_size
        )
    
    def print_opensearch_info(self):
        try:
            info = self.client.info()
            logger.info(f"OpenSearch Version: {info.get('version', {}).get('number')}")
            logger.info(f"Cluster Name: {info.get('cluster_name')}")
            logger.info(f"Cluster UUID: {info.get('cluster_uuid')}")
            return info
        except Exception as e:
            logger.error(f"Error getting OpenSearch info: {e}")
            raise
    
    def index_chunk_embeddings(self, chunks: List[str], chunk_embeddings: List[List[float]], 
                              indexing_algorithm: str, chunking_algorithm: str,
                              vector_dimension: int, metadata: List[Dict] = None, 
                              chunk_size: int = 1200):
        return self.client.index_chunk_embeddings(
            chunks, chunk_embeddings, indexing_algorithm, chunking_algorithm,
            vector_dimension, metadata, chunk_size
        )
