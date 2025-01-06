import logging
from typing import Dict, List

from core.embedding import EmbedderFactory
from . import BedrockEmbedder

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CohereEmbedder(BedrockEmbedder):
    def prepare_payload(self, text: str, dimensions: int, normalize: bool) -> Dict:
        return {"texts": [text], "input_type": "search_document"}

    def extract_embedding(self, response: Dict) -> List[float]:
        return response["embeddings"][0]


EmbedderFactory.register_embedder("bedrock", "cohere.embed-english-v3", CohereEmbedder)
EmbedderFactory.register_embedder("bedrock", "cohere.embed-multilingual-v3", CohereEmbedder)
