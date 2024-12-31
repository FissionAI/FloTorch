from typing import List
from baseclasses.base_classes import BaseChunker
from langchain.text_splitter import RecursiveCharacterTextSplitter

class HierarchicalChunker(BaseChunker):
    """Hierarchical chunking strategy."""

    def chunk(self, text: str) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        return splitter.split_text(text)
