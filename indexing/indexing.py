import logging
import re
import uuid

from baseclasses.base_pipeline import BasePipeline
from core.opensearch_vectorstore import OpenSearchVectorDatabase
from core.processors import ChunkingProcessor, EmbedProcessor
from util.pdf_utils import process_pdf_from_folder
from util.s3util import S3Util
from opensearchpy.helpers import bulk

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Indexer(BasePipeline):
    def execute(self) -> None:
        """Main function to run the chunking and embedding pipeline."""
        experiment_dynamodb = self.components['experiment_dynamodb']
        logger.info(experiment_dynamodb.table)

        try:
            if not self.experimentalConfig.kb_data:
                raise ValueError("S3 path is missing in the kb_data field.")

            # Step 1: Download PDF folder from S3
            pdf_folder_path = S3Util().download_directory_from_s3(self.experimentalConfig.kb_data)

            # Step 2: Chunking
            chunks = ChunkingProcessor(self.experimentalConfig).chunk([process_pdf_from_folder(pdf_folder_path)])
            # Step 3: Embedding
            embedding_results = EmbedProcessor(self.experimentalConfig).embed(chunks)

            #total_index_embed_tokens = sum(int(metadata['inputTokens']) for _, _, metadata in embedding_results)
            # Process hierarchical chunking
            documents = self.prepare_documents(embedding_results.embedList, chunks, embedding_results.input_tokens)

            logger.info(
                f"Experiment {self.experimentalConfig.experiment_id} Indexing Embed Tokens : {embedding_results.input_tokens}")

            self.log_dynamodb_update(embedding_results.input_tokens, 0, 0)
            self._insert_to_opensearch(documents)

        except Exception as e:
            logger.exception(f"Pipeline failed: {e}")
            raise e

    def prepare_documents(self, embedding_results, chunks, total_index_embed_tokens):
        """Prepare documents for OpenSearch indexing."""
        if self.experimentalConfig.is_hierarchical():
            temp_results = []
            for i, chunk in enumerate(chunks):
                temp_embedding = list(embedding_results[i])
                temp_embedding.extend([chunk.chunk, chunk.child_chunk])
                temp_results.append(temp_embedding)
            embedding_results = temp_results
            documents = [
                {
                    "_index": self.experimentalConfig.index_id,
                    "execution_id": self.experimentalConfig.execution_id,
                    "chunk_id": str(uuid.uuid4()),  # Generate a unique UUID for each chunk
                    "text": self.clean_text_for_vector_db(parent_chunk),
                    "child_text": self.clean_text_for_vector_db(chunk),
                    "parent_id": parent_id,
                    self.config.vector_field: embedding,
                    "metadata": metadata  # Optional metadata, defaulting to an empty dictionary
                }
                for embedding, chunk, metadata, parent_id, parent_chunk in embedding_results
                # Enumerate is unnecessary since UUIDs are used
            ]
        else:
            documents = [
                {
                    "_index": self.experimentalConfig.index_id,
                    "execution_id": self.experimentalConfig.execution_id,
                    "chunk_id": str(uuid.uuid4()),  # Generate a unique UUID for each chunk
                    "text": self.clean_text_for_vector_db(chunk),
                    self.config.vector_field: embedding,
                    "metadata": metadata  # Optional metadata, defaulting to an empty dictionary
                }
                for embedding, chunk, metadata in embedding_results  # Enumerate is unnecessary since UUIDs are used
            ]

        logger.info(f"Experiment {self.experimentalConfig.experiment_id} Indexing Embed Tokens : {total_index_embed_tokens}")
        return documents

    def clean_text_for_vector_db(self, text):
        """Cleans the input text for vector database."""
        text = text.replace('"', '').replace("'", "")
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        text = text.replace('\n', ' ').replace('\t', ' ')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _insert_to_opensearch(self, documents):
        vector_database = OpenSearchVectorDatabase(host=self.config.opensearch_host, is_serverless=self.config.opensearch_serverless, region=self.config.aws_region,username=self.config.opensearch_username,
            password=self.config.opensearch_password)
        chunks_length = len(documents)
        chunk_size = 500 # Default chunk size streaming by Opensearch
        if chunks_length < chunk_size:
            chunk_size = chunks_length
        logger.info(f"Opensearch Bulk insert initiated")
        bulk(vector_database.client, documents, chunk_size=chunk_size, max_retries=1)
        logger.info("Opensearch Bulk insert successful \n Pipeline completed successfully.")
