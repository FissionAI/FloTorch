import logging
from typing import Dict, List
from core.chunking import Chunk
from core.embedding.embedding_factory import EmbedderFactory

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Embed:
    """Class to encapsulate the embedding result with metadata and chunk."""

    def __init__(self, embedding: List[float], text: str, metadata: Dict[str, str]) -> None:
        self.embedding = embedding
        self.text = text
        self.metadata = metadata

    def __repr__(self) -> str:
        return f"Embed(text={self.text[:50]}, embedding=[...] , metadata={self.metadata})"

    def input_tokens(self):
        try:
            input_tokens = self.metadata.get('inputTokens', None)
            if input_tokens is None:
                return 0
            return int(input_tokens)
        except (ValueError, TypeError):
            return 0


class EmbedList:
    def __init__(self):
        self.embed_list = []
        self.input_tokens = 0

    def append(self, embed: Embed):
        self.embed_list.append(embed)
        self.input_tokens += embed.input_tokens()


class EmbedProcessor:
    """Processor for embedding text chunks."""

    def __init__(
        self,
        service_type: str,
        model_id: str,
        aws_region: str,
        role_arn: str,
        vector_dimension: int,
        normalize: bool = True
    ) -> None:
        self.service_type = service_type
        self.model_id = model_id
        self.aws_region = aws_region
        self.role_arn = role_arn
        self.vector_dimension = vector_dimension
        self.normalize = normalize

        # Create the embedder instance
        self.embedder = EmbedderFactory.create_embedder(
            service_type=service_type,
            model_id=model_id,
            aws_region=aws_region,
            role_arn=role_arn
        )

    def embed(self, chunks: List[Chunk]) -> EmbedList:
        """Embed each chunk one by one."""
        embeddings = EmbedList()
        try:
            logger.info(f"Embedding {len(chunks)} chunks with dimensions: {self.vector_dimension}.")
            for idx, chunk in enumerate(chunks):
                logger.debug(f"Embedding chunk {idx + 1}/{len(chunks)}: {chunk.chunk[:50]}...")
                metadata, embedding = self.embedder.embed(
                    chunk.chunk,
                    dimensions=self.vector_dimension,
                    normalize=self.normalize
                )
                embed = Embed(embedding, text=chunk.chunk, metadata=metadata)
                embeddings.append(embed)

            logger.info("Embedding process completed successfully.")
            return embeddings
        except Exception as e:
            logger.error(f"Error during embedding process: {e}")
            raise

    def embed_text(self, text: str) -> Embed:
        """Embed text and return an Embed object."""
        try:
            metadata, embedding = self.embedder.embed(
                text,
                dimensions=self.vector_dimension,
                normalize=self.normalize
            )
            embed = Embed(embedding, text=text, metadata=metadata)
            logger.info("Embedding text process completed successfully.")
            return embed
        except Exception as e:
            logger.error(f"Error during embedding process: {e}")
            raise