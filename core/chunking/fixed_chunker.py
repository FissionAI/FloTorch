from typing import List

from langchain.text_splitter import CharacterTextSplitter

from baseclasses.base_classes import BaseChunker


class FixedChunker(BaseChunker):
    """Fixed chunking strategy using LangChain’s CharacterTextSplitter."""

    def chunk(self, text : str) -> List[str]:
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        if not text:
            raise ValueError("Input text cannot be empty or None")
        
        # TODO: Temporary fix, better to move to recursive
        separators = [' ', '\t', '\n', '\r', '\f', '\v']
        for sep in separators:
            text = text.replace(sep, ' ')

        # chunk size is in tokens, general norm : 1 token = 4 chars
        chunk_size = 4 * self.chunk_size
        # overlap is in percentage
        chunk_overlap = int(self.chunk_overlap * chunk_size / 100)
        self.text_splitter = CharacterTextSplitter(
            separator=" ",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False
        )
        chunks = self.text_splitter.split_text(text)
        return chunks