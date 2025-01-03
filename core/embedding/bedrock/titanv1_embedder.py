import logging
from typing import Dict, List

from core.embedding import EmbedderFactory
from . import BedrockEmbedder

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TitanV1Embedder(BedrockEmbedder):
    def prepare_payload(self, text: str, dimensions: int, normalize: bool) -> Dict:
        return {"inputText": text}

    def extract_embedding(self, response: Dict) -> List[float]:
        return response["embedding"]


EmbedderFactory.register_embedder("bedrock", "amazon.titan-embed-text-v1", TitanV1Embedder)
EmbedderFactory.register_embedder("bedrock", "amazon.titan-embed-image-v1", TitanV1Embedder)
