from core.processors import ChunkingProcessor, EmbedProcessor
from core.opensearch_vectorstore import OpenSearchVectorDatabase
from util.s3util import S3Util
from util.pdf_utils import extract_text_from_pdf 
import logging
from typing import Dict, List, Any
from opensearchpy.helpers import bulk
import os
import uuid
import json
from config.experimental_config import ExperimentalConfig
from config.config import Config
from core.dynamodb import DynamoDBOperations

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def chunk_embed_store(config : Config, experimentalConfig : ExperimentalConfig)-> None:
    """Main function to run the chunking and embedding pipeline."""
    experiment_dynamodb = DynamoDBOperations(region=config.aws_region, table_name=config.experiment_table)
    logger.info(experiment_dynamodb.table)
    try:
        """Main function to run the pipeline."""
        
        if not experimentalConfig.kb_data:
            raise ValueError("S3 path is missing in the kb_data field.")
        
        pdf_file_path = S3Util().download_file_from_s3(experimentalConfig.kb_data)
        
        # Step 1: Chunking
        chunks = ChunkingProcessor(experimentalConfig).chunk(extract_text_from_pdf(pdf_file_path))
        
        # Step 2: Embedding
        embedding_results = EmbedProcessor(experimentalConfig).embed(chunks)
        documents = [
            {
                "_index": experimentalConfig.index_id,
                "execution_id":experimentalConfig.execution_id,
                "chunk_id": str(uuid.uuid4()),  # Generate a unique UUID for each chunk
                "text": chunk,
                config.vector_field: embedding,
                "metadata": {}  # Optional metadata, defaulting to an empty dictionary
            }
            for embedding, chunk in embedding_results  # Enumerate is unnecessary since UUIDs are used
        ]

        _insert_to_opensearch(config, documents)
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        raise e
    
def _insert_to_opensearch(config: Config, documents: List[Dict[str, Any]]):
    vector_database = OpenSearchVectorDatabase(host=config.opensearch_host, is_serverless=config.opensearch_serverless, region=config.aws_region,username=config.opensearch_username,
        password=config.opensearch_password)
    chunks_length = len(documents)
    chunk_size = 500 # Default chunk size streaming by Opensearch
    if chunks_length < chunk_size:
        chunk_size = chunks_length
    bulk(vector_database.client, documents, chunk_size=chunk_size, max_retries=1)
    logger.info("Pipeline completed successfully.")




