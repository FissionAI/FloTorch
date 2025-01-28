from typing import List, Dict, Any, Union
import boto3
import logging
from baseclasses.base_classes import VectorDatabase
from config.config import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class KnowledgeBaseVectorDatabase(VectorDatabase):
    def __init__(self, region: str = 'us-east-1'):
        self.client = boto3.client("bedrock-agent-runtime", region_name=region)
        
    def create_index(self, index_name: str, mapping: Dict[str, Any], algorithm: str) -> None:
        raise NotImplementedError("This method is not implemented in this minimal version.")

    def update_index(self, index_name: str, new_mapping: Dict[str, Any]) -> None:
        raise NotImplementedError("This method is not implemented in this minimal version.")

    def delete_index(self, index_name: str) -> None:
        raise NotImplementedError("This method is not implemented in this minimal version.")

    def insert_document(self, index_name: str, document: Dict[str, Any]) -> None:
        raise NotImplementedError("This method is not implemented in this minimal version.")
    
    
    def _format_response(self, data):
        formatted_results = []
        
        for result in data.get('retrievalResults', []):
            content = result.get('content', {})
            text = content.get('text', '')
            
            if text:
                formatted_results.append({'text': text})
        
        return formatted_results

    def search(self, query: str, kb_data: str,  knn: int):
        query = {"text": query}
        retrievalConfiguration={
        'vectorSearchConfiguration': {
            'numberOfResults': knn
            }
        }
        response = self.client.retrieve(knowledgeBaseId = kb_data, 
                                        retrievalQuery = query, 
                                        retrievalConfiguration=retrievalConfiguration)
        formatted_context = self._format_response(response)
        logger.info("Getting results from knowledge base")
        return formatted_context
        