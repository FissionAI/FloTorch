import unittest
from unittest.mock import MagicMock, patch
from core.chunking import Chunk
from core.processors.embed_processor import EmbedProcessor, Embed, EmbedList


class TestEmbedProcessor(unittest.TestCase):

    @patch("core.embedding.embedding_factory.EmbedderFactory.create_embedder")
    def setUp(self, mock_create_embedder):
        """Set up the test environment and mock dependencies."""
        self.service_type = "test_service"
        self.model_id = "test_model"
        self.aws_region = "test_region"
        self.role_arn = "test_role"
        self.vector_dimension = 128
        self.normalize = True

        # Mock embedder
        self.mock_embedder = MagicMock()
        mock_create_embedder.return_value = self.mock_embedder

        # Initialize the EmbedProcessor
        self.embed_processor = EmbedProcessor(
            service_type=self.service_type,
            model_id=self.model_id,
            aws_region=self.aws_region,
            role_arn=self.role_arn,
            vector_dimension=self.vector_dimension,
            normalize=self.normalize
        )

    def test_embed_text_success(self):
        """Test the embed_text method for successful embedding."""
        # Mock the embedder's embed method
        mock_metadata = {"inputTokens": "10"}
        mock_embedding = [0.1, 0.2, 0.3]
        self.mock_embedder.embed.return_value = (mock_metadata, mock_embedding)

        # Call the method
        text = "Test text for embedding."
        result = self.embed_processor.embed_text(text)

        # Assertions
        self.mock_embedder.embed.assert_called_once_with(
            text, dimensions=self.vector_dimension, normalize=self.normalize
        )
        self.assertIsInstance(result, Embed)
        self.assertEqual(result.text, text)
        self.assertEqual(result.embedding, mock_embedding)
        self.assertEqual(result.metadata, mock_metadata)

    def test_embed_text_failure(self):
        """Test the embed_text method when an error occurs."""
        self.mock_embedder.embed.side_effect = Exception("Mocked embedding error")

        # Call the method and assert an exception is raised
        with self.assertRaises(Exception) as context:
            self.embed_processor.embed_text("Test text")

        self.assertEqual(str(context.exception), "Mocked embedding error")

    def test_embed_chunks_success(self):
        """Test the embed method for embedding a list of chunks."""
        # Mock the embedder's embed method
        mock_metadata = {"inputTokens": "5"}
        mock_embedding = [0.1, 0.2, 0.3]
        self.mock_embedder.embed.return_value = (mock_metadata, mock_embedding)

        # Create mock chunks
        chunks = [
            Chunk(id="1", chunk="First chunk", child_chunk="First chunk"),
            Chunk(id="2", chunk="Second chunk", child_chunk="Second chunk"),
        ]

        # Call the method
        result = self.embed_processor.embed(chunks)

        # Assertions
        self.assertIsInstance(result, EmbedList)
        self.assertEqual(len(result.embed_list), 2)
        self.assertEqual(result.input_tokens, 10)  # 5 + 5 from mock_metadata

        # Check individual embeddings
        for idx, embed in enumerate(result.embed_list):
            self.assertIsInstance(embed, Embed)
            self.assertEqual(embed.text, chunks[idx].chunk)
            self.assertEqual(embed.embedding, mock_embedding)
            self.assertEqual(embed.metadata, mock_metadata)

    def test_embed_chunks_failure(self):
        """Test the embed method when an error occurs."""
        self.mock_embedder.embed.side_effect = Exception("Mocked embedding error")

        # Create mock chunks
        chunks = [
            Chunk(id="1", chunk="First chunk", child_chunk="First chunk"),
        ]

        # Call the method and assert an exception is raised
        with self.assertRaises(Exception) as context:
            self.embed_processor.embed(chunks)

        self.assertEqual(str(context.exception), "Mocked embedding error")


if __name__ == "__main__":
    unittest.main()