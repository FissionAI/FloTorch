from typing import Dict, List, Type
from core.chunking import FixedChunker, HierarchicalChunker
from baseclasses.base_classes import BaseChunker
import logging
from config.experimental_config import ExperimentalConfig

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class ChunkingProcessor:
    """Processor for managing text chunking."""

    CHUNKER_STRATEGIES: Dict[str, Type[BaseChunker]] = {
        "Fixed": FixedChunker,
        "Hierarchical": HierarchicalChunker
    }

    def __init__(self,  experimentalConfig : ExperimentalConfig) -> None:
        self.experimentalConfig = experimentalConfig
        self.chunker = self._initialize_chunker()

    def _initialize_chunker(self) -> BaseChunker:
        """Initialize the chunker based on the selected strategy."""
        strategy = self.experimentalConfig.chunking_strategy.lower()  # Normalize to lower case
        chunker_strategies = {key.lower(): value for key, value in self.CHUNKER_STRATEGIES.items()}  # Case-insensitive map
        if strategy not in chunker_strategies:
            raise ValueError(f"Unknown chunking strategy: {strategy}")

        logger.info(f"Initializing {strategy} chunker...")
        return chunker_strategies[strategy](
            self.experimentalConfig.chunk_size,
            self.experimentalConfig.chunk_overlap
        )

    def chunk(self, texts: List[str]) -> List[str]:
        """Chunk the input list of text into a single flat list"""
        all_chunks = [chunk for text in texts for chunk in self.chunker.chunk(text)]
        return all_chunks