import logging
from typing import Dict, List, Union

from core.embedding import EmbedderFactory
from core.embedding.sagemaker.sagemaker_embedder import SageMakerEmbedder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class BGEEndpointSageMakerEmbedder(SageMakerEmbedder):
    def prepare_payload(self, texts: Union[str, List[str]], dimensions: int, normalize: bool) -> Dict:
        if isinstance(texts, str):
            texts = [texts]
        return {
            "inputs": texts,
            "parameters": {
                "normalize": normalize
            }
        }
        
    def embed(self, text: Union[str, List[str]], dimensions: int = 1024, normalize: bool = True) -> Union[List[float], List[List[float]]]:
        payload = self.prepare_payload(text, dimensions, normalize)
        response = self.predictor.predict(payload)
        embeddings = self.extract_embedding(response)
        return embeddings[0] if isinstance(text, str) else embeddings
    
    def extract_embedding(self, response: Union[List[float], List[List[float]], Dict]) -> Union[List[float], List[List[float]]]:
        """Extract embedding from the response"""
        if isinstance(response, list):
            return response
        
        if isinstance(response, dict) and "embeddings" in response:
            return response["embeddings"]
            
        raise ValueError(f"Unexpected response format: {type(response)}. Response: {response}")

# Register the embedder
EmbedderFactory.register_embedder("sagemaker", "BAAI/bge-large-en-v1.5", BGEEndpointSageMakerEmbedder)