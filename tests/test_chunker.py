import unittest

from core.chunking import FixedChunker, Chunk, HierarchicalChunker


class TestChunking(unittest.TestCase):
    def setUp(self):
        """Set up default parameters for chunkers."""
        self.text = (
            "this is testing text."
        )
        self.chunk_size = 10  # tokens
        self.chunk_overlap = 20  # percentage
        self.child_chunk_size = 5  # tokens

    def test_fixed_chunker_invalid_chunk_size(self):
        """Test FixedChunker with invalid chunk size."""
        with self.assertRaises(ValueError) as cm:
            FixedChunker(chunk_size=0, chunk_overlap=self.chunk_overlap).chunk(self.text)
        self.assertEqual(str(cm.exception), "chunk_size must be positive")

    def test_fixed_chunker_invalid_overlap(self):
        """Test FixedChunker with overlap >= chunk_size."""
        with self.assertRaises(ValueError) as cm:
            FixedChunker(chunk_size=self.chunk_size, chunk_overlap=100).chunk(self.text)
        self.assertEqual(str(cm.exception), "chunk_overlap must be less than chunk_size")

    def test_hierarchical_chunker_valid_input(self):
        """Test HierarchicalChunker with valid input."""
        chunker = HierarchicalChunker(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            child_chunk_size=self.child_chunk_size
        )
        chunks = chunker.chunk(self.text)
        self.assertIsInstance(chunks, list)
        self.assertTrue(all(isinstance(chunk, Chunk) for chunk in chunks))

    def test_hierarchical_chunker_invalid_parent_chunk_size(self):
        """Test HierarchicalChunker with invalid parent chunk size."""
        with self.assertRaises(ValueError) as cm:
            HierarchicalChunker(
                chunk_size=0,
                chunk_overlap=self.chunk_overlap,
                child_chunk_size=self.child_chunk_size
            ).chunk(self.text)
        self.assertEqual(str(cm.exception), "Both parent and child chunk sizes must be positive.")

    def test_hierarchical_chunker_invalid_child_chunk_size(self):
        """Test HierarchicalChunker with invalid child chunk size."""
        with self.assertRaises(ValueError) as cm:
            HierarchicalChunker(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                child_chunk_size=0
            ).chunk(self.text)
        self.assertEqual(str(cm.exception), "Both parent and child chunk sizes must be positive.")

    def test_hierarchical_chunker_child_greater_than_parent(self):
        """Test HierarchicalChunker when child chunk size is greater than parent."""
        with self.assertRaises(ValueError) as cm:
            HierarchicalChunker(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                child_chunk_size=self.chunk_size + 1
            ).chunk(self.text)
        self.assertEqual(str(cm.exception), "Child chunk size must be smaller than parent chunk size.")

    def test_hierarchical_chunker_invalid_overlap(self):
        """Test HierarchicalChunker with overlap >= child chunk size."""
        with self.assertRaises(ValueError) as cm:
            HierarchicalChunker(
                chunk_size=self.chunk_size,
                chunk_overlap=100,
                child_chunk_size=self.child_chunk_size
            ).chunk(self.text)
        self.assertEqual(str(cm.exception), "chunk_overlap must be less than child chunk size.")

    def test_hierarchical_chunker_empty_text(self):
        """Test HierarchicalChunker with empty input."""
        chunker = HierarchicalChunker(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            child_chunk_size=self.child_chunk_size
        )
        with self.assertRaises(ValueError) as cm:
            chunker.chunk("")
        self.assertEqual(str(cm.exception), "Input text cannot be empty or None")


if __name__ == "__main__":
    unittest.main()