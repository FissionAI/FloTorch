from abc import abstractmethod, ABC
from typing import List
from langchain.text_splitter import CharacterTextSplitter
import uuid


class Chunk:
    """A class to hold the parent and child chunk details."""
    def __init__(self, id: str, chunk: str, child_chunk: str) -> None:
        self.id = id
        self.chunk = chunk
        self.child_chunk = child_chunk

class BaseChunker(ABC):
    """Abstract base class for chunking strategies."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def __init__(self, chunk_size: int,  chunk_overlap: int, child_chunk_size: int) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.child_chunk_size = child_chunk_size

    @abstractmethod
    def chunk(self, text: str) -> List[Chunk]:
        """Abstract method for chunking text."""
        pass

class FixedChunker(BaseChunker):
    """Fixed chunking strategy using LangChain’s CharacterTextSplitter."""

    def chunk(self, text: str) -> List[Chunk]:
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        if not text:
            raise ValueError("Input text cannot be empty or None")

        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ',)  # Replace common separators

        # chunk size is in tokens, general norm: 1 token = 4 chars
        chunk_size = 4 * self.chunk_size
        chunk_overlap = int(self.chunk_overlap * chunk_size / 100)

        text_splitter = CharacterTextSplitter(
            separator=" ",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False
        )

        # Now return chunks as List[Chunk]
        parent_chunks = text_splitter.split_text(text)
        overall_chunks = []
        for parent_chunk in parent_chunks:
            parent_id = str(uuid.uuid4())  # For FixedChunker, parent and child are the same
            overall_chunks.append(Chunk(parent_id, parent_chunk, parent_chunk))
        return overall_chunks


class HierarchicalChunker(BaseChunker):
    """Hierarchical chunking strategy using BaseChunker."""

    def chunk(self, text: str) -> List[Chunk]:
        overlap_tokens = int((self.chunk_overlap / 100) * self.child_chunk_size)
        if self.chunk_size <= 0 or self.child_chunk_size <= 0:
            raise ValueError("Both parent and child chunk sizes must be positive.")
        if self.child_chunk_size > self.chunk_size:
            raise ValueError("Child chunk size must be smaller than parent chunk size.")
        if overlap_tokens >= self.child_chunk_size:
            raise ValueError("chunk_overlap must be less than child chunk size.")
        if not text:
            raise ValueError("Input text cannot be empty or None")

        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ',)  # Replace common separators

        parent_character_chunk_size = 4 * self.chunk_size
        child_character_chunk_size = 4 * self.child_chunk_size
        child_chunk_overlap_characters = int(self.chunk_overlap * child_character_chunk_size / 100)

        parent_text_splitter = CharacterTextSplitter(
            separator=" ",
            chunk_size=parent_character_chunk_size,
            chunk_overlap=0,
            length_function=len,
            is_separator_regex=False
        )

        child_text_splitter = CharacterTextSplitter(
            separator=" ",
            chunk_size=child_character_chunk_size,
            chunk_overlap=child_chunk_overlap_characters,
            length_function=len,
            is_separator_regex=False
        )

        parent_chunks = parent_text_splitter.split_text(text)
        overall_chunks = []

        for parent_chunk in parent_chunks:
            parent_id = str(uuid.uuid4())
            child_chunks = child_text_splitter.split_text(parent_chunk)
            for child_chunk in child_chunks:
                overall_chunks.append(Chunk(parent_id, parent_chunk, child_chunk))

        return overall_chunks