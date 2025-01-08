import logging
from typing import Dict, List, Any
from config.experimental_config import ExperimentalConfig
from core.chunking import Chunk
from core.embedding import EmbedderFactory

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Embed:
    """Class to encapsulate the embedding result with metadata and chunk."""

    def __init__(self, embedding:[float], chunk: Chunk) -> None:
        self.embedding = embedding
        self.chunk = chunk

    def __init__(self, embedding:[float], text: str) -> None:
        self.embedding = embedding
        self.text = text

    def __repr__(self) -> str:
        return f"Embed(chunk={self.chunk}, embedding=[...] , metadata={self.metadata})"


class EmbedProcessor:
    """Processor for embedding text chunks."""

    def __init__(self, experimentalConfig: ExperimentalConfig) -> None:
        self.experimentalConfig = experimentalConfig
        self.embedder = EmbedderFactory.create_embedder(experimentalConfig)

    def embed(self, chunks: List[Chunk]) -> List[Embed]:
        """Embed each chunk one by one."""
        embeddings = []
        try:
            dimensions = self.experimentalConfig.vector_dimension
            normalize = True  # Always normalize

            logger.info(f"Embedding {len(chunks)} chunks with dimensions: {dimensions}.")
            for idx, chunk in enumerate(chunks):
                logger.debug(f"Embedding chunk {idx + 1}/{len(chunks)}: {chunk[:50]}...")
                embedding = self.embedder.embed(chunk.chunk, dimensions=dimensions, normalize=normalize)
                embed = Embed(embedding, chunk=chunk)
                embeddings.append(embed)

            logger.info("Embedding process completed successfully.")
            return embeddings
        except Exception as e:
            logger.error(f"Error during embedding process: {e}")
            raise

    def embed_text(self, text: str) -> Embed:
        """Embed text and return an Embed object."""
        try:
            dimensions = self.experimentalConfig.vector_dimension
            normalize = True  # Always normalize
            embedding = self.embedder.embed(text, dimensions=dimensions, normalize=normalize)
            embed = Embed(embedding, text)
            logger.info("Embedding text process completed successfully.")
            return embed
        except Exception as e:
            logger.error(f"Error during embedding process: {e}")
            raise