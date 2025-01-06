import uuid
from typing import List

from langchain.text_splitter import CharacterTextSplitter

from baseclasses.base_classes import BaseHierarchicalChunker


class HierarchicalChunker(BaseHierarchicalChunker):
    """Hierarchical chunking strategy."""

    def chunk(self, text: str) -> List[List[str]]:
        overlap_tokens = int((self.chunk_overlap / 100) * self.child_chunk_size)
        if self.parent_chunk_size <= 0:
            raise ValueError("parent chunk size must be positive")
        if self.child_chunk_size <= 0:
            raise ValueError("child chunk size must be positive")
        if self.child_chunk_size > self.parent_chunk_size:
            raise ValueError("child chunk size must be less than parent chunk size")
        if overlap_tokens >= self.child_chunk_size:
            raise ValueError("chunk_overlap must be less than child chunk size")
        if not text:
            raise ValueError("Input text cannot be empty or None")

        # TODO: Temporary fix, better to move to recursive
        separators = [' ', '\t', '\n', '\r', '\f', '\v']
        for sep in separators:
            text = text.replace(sep, ' ')

        # chunk size is in tokens, general norm : 1 token = 4 chars
        parent_character_chunk_size = 4 * self.parent_chunk_size
        child_character_chunk_size = 4 * self.child_chunk_size
        # overlap is in percentage
        child_chunk_overlap_characters = int(self.chunk_overlap * child_character_chunk_size / 100)
        self.parent_text_splitter = CharacterTextSplitter(
            separator=" ",
            chunk_size=parent_character_chunk_size,
            chunk_overlap=0,  # Can change this at a later point of time
            length_function=len,
            is_separator_regex=False
        )
        self.child_text_splitter = CharacterTextSplitter(
            separator=" ",
            chunk_size=child_character_chunk_size,
            chunk_overlap=child_chunk_overlap_characters,
            length_function=len,
            is_separator_regex=False
        )
        parent_chunks = self.parent_text_splitter.split_text(text)
        overall_chunks = []
        for parent_chunk in parent_chunks:
            parent_id = str(uuid.uuid4())
            child_chunks = self.child_text_splitter.split_text(parent_chunk)
            for child_chunk in child_chunks:
                temp_chunk = (parent_id, parent_chunk, child_chunk)
                overall_chunks.append(temp_chunk)
        return overall_chunks
