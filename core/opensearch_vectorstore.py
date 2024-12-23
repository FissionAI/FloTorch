import traceback, json
from typing import Dict, Any, List, Optional
from botocore.endpoint import uuid
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from baseclasses.base_classes import VectorDatabase
import boto3
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

class OpenSearchVectorDatabase(VectorDatabase):
    def __init__(self, host: str, use_ssl: bool = True, port: int = 443, is_serverless : bool = True, region: str = 'us-east-1', username: str = None, password: str = None):
        if is_serverless:
            try:
                # Get credentials from the Lambda role
                credentials = boto3.Session().get_credentials()
                # Create AWS V4 Signer Auth for OpenSearch Serverless
                auth = AWSV4SignerAuth(credentials, region, 'aoss')
                
                # Initialize OpenSearch client for serverless
                self.client = OpenSearch(
                    hosts=[{'host': host, 'port': port}],
                    http_auth=auth,
                    use_ssl=True,  
                    verify_certs=True,
                    connection_class=RequestsHttpConnection,
                    timeout=30,
                    max_retries=3,
                    retry_on_timeout=True,
                    # Add required headers for OpenSearch Serverless
                    headers={
                        'host': host
                    }
                )
                
            except Exception as e:
                logger.error(f"Failed to initialize OpenSearch Serverless client: {str(e)}", exc_info=True)
                raise
        else:
            self.client = OpenSearch(
                hosts=[{'host': host, 'port': port}],
                http_auth=(username, password),
                use_ssl=use_ssl,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
                timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )

    def _get_algorithm_settings(self, algorithm: str, dim: int) -> Dict[str, Any]:
        
        base_hnsw_params = {
            "ef_construction": 512,
            "m": 16
        }

        if algorithm == "hnsw":
            return {
                "name": "hnsw",
                "engine": "faiss",
                "space_type": "innerproduct",
                "parameters": base_hnsw_params
            }   
        elif algorithm == "hnsw_sq":
            return {
                "name": "hnsw",
                "engine": "faiss",
                "space_type": "innerproduct",
                "parameters": {
                    **base_hnsw_params,
                    "encoder": {
                        "name": "sq",
                        "parameters": {
                            "type": "fp16"
                        }
                    }
                }
            }
        elif algorithm == "hnsw_bq":
            return {
                "name": "hnsw",
                "engine": "faiss",
                "space_type": "innerproduct",
                "parameters": base_hnsw_params
            }
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    
    def create_index(self, index_name: str, mapping: Dict[str, Any], algorithm: str) -> None:
        vector_field = next((field for field, props in mapping['properties'].items() 
                             if props['type'] == 'knn_vector'), None)
        if not vector_field:
            raise ValueError("Mapping must include a knn_vector field")
    
        dim = mapping['properties'][vector_field]['dimension']
        algorithm_settings = self._get_algorithm_settings(algorithm, dim)
    
        index_body = {
            "settings": {
                "index": {
                    "knn": True,
                    "knn.algo_param.ef_search": 100
                }
            },
            "mappings": {
                "properties": {
                    vector_field: {
                        "type": "knn_vector",
                        "dimension": dim,
                        "method": algorithm_settings,
                        **({"mode": "on_disk"} if algorithm == "hnsw_bq" else {})
                    }
                }
            }
        }
    
        # Add other fields from the original mapping
        for field, props in mapping['properties'].items():
            if field != vector_field:
                index_body["mappings"]["properties"][field] = props
    
        logger.info(f"Creating index '{index_name}' with body:")
        logger.info(json.dumps(index_body, indent=2))
    
        try:
            self.client.indices.create(index=index_name, body=index_body)
            logger.info(f"Successfully created index '{index_name}'")
        except Exception as e:
            logger.error(f"Error creating index '{index_name}': {str(e)}")
            logger.error(f"Index body: {json.dumps(index_body, indent=2)}")
            traceback.print_exc()
            raise
    

    def update_index(self, index_name: str, new_mapping: Dict[str, Any]) -> None:
        self.client.indices.put_mapping(index=index_name, body=new_mapping)

    def delete_index(self, index_name: str) -> None:
        self.client.indices.delete(index=index_name)

    def insert_document(self, index_name: str, document: Dict[str, Any]) -> None:
        self.client.index(index=index_name, body=document)

    def search(self, index_name: str, query_vector: List[float], k: int) -> List[Dict[str, Any]]:
        vector_field = next((field for field, props in 
                             self.client.indices.get_mapping(index=index_name)[index_name]['mappings']['properties'].items() 
                             if 'type' in props and props['type'] == 'knn_vector'), None)
        if not vector_field:
            raise ValueError("Index does not contain a knn_vector field")

        query = {
            "size": k,
            "query": {
                "knn": {
                    vector_field: {
                        "vector": query_vector,
                        "k": k
                    }
                }
            },
            "_source": True,
            "fields" : ["text"]
        }

        response = self.client.search(index=index_name, body=query)
        return [hit['_source'] for hit in response['hits']['hits']]
    
    def index_exists(self, index_name: str) -> bool:
        """
        Check if an index exists in OpenSearch.

        :param index_name: Name of the index to check
        :return: True if the index exists, False otherwise
        """
        return self.client.indices.exists(index=index_name)
    
    def insert_chunk(self, index_name: str, text: str, embedding: List[float], chunk_id: str, metadata: Dict = None):
        document = {
            "text": text,
            "embedding": embedding,
            "chunk_id": chunk_id,
            "metadata": metadata or {}
        }
        try:
            self.insert_document(index_name, document)
        except Exception as e:
            logger.error(f"Error inserting chunk {chunk_id}: {str(e)}")

    def batch_insert_chunks(self, index_name: str, chunks: List[str], chunk_embeddings: List[List[float]], 
                            metadata: Optional[List[Dict]] = None, batch_size: int = 100):
        total_chunks = len(chunks)
        
        # If metadata is None or empty, create a list of empty dictionaries
        if not metadata:
            metadata = [{} for _ in range(total_chunks)]
        
        for i in range(0, total_chunks, batch_size):
            batch_chunks = chunks[i:i+batch_size]
            batch_embeddings = chunk_embeddings[i:i+batch_size]
            batch_metadata = metadata[i:i+batch_size]
            
            for chunk, embedding, meta in zip(batch_chunks, batch_embeddings, batch_metadata):
                chunk_id = str(uuid.uuid4())  # Generate a unique ID for each chunk
                self.insert_chunk(index_name, chunk, embedding, chunk_id, meta)
            
            logger.info(f"Inserted batch {i//batch_size + 1} ({i+1} to {min(i+batch_size, total_chunks)} of {total_chunks})")
    

    def print_opensearch_info(self):
        try:
            info = self.client.info()
            logger.info(f"OpenSearch Version: {info['version']['number']}")
            logger.info(f"Cluster Name: {info['cluster_name']}")
            logger.info(f"Cluster UUID: {info['cluster_uuid']}")
        except Exception as e:
            logger.error(f"Error getting OpenSearch info: {str(e)}")
    

    def index_chunk_embeddings(self, chunks: List[str], chunk_embeddings: List[List[float]], 
                           indexing_algorithm: str, chunking_algorithm: str,
                           vector_dimension: int, metadata: List[Dict] = None, chunk_size: int = 1200):
        index_name = f"{indexing_algorithm}-{chunking_algorithm.lower()}-{chunk_size}"
        
        mapping = {
            "properties": {
                "text": {"type": "text"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": vector_dimension
                },
                "metadata": {"type": "object"}
            }
        }

        try:
            self.print_opensearch_info()  # Print OpenSearch version and cluster info
            self.create_index(index_name, mapping, indexing_algorithm)
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            return
    
        self.batch_insert_chunks(index_name, chunks, chunk_embeddings, metadata)
        return f"Indexing complete for '{index_name}'!"