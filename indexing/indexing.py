from core.processors import ChunkingProcessor, EmbedProcessor
from core.opensearch_vectorstore import OpenSearchVectorDatabase
from util.s3util import S3Util
from util.pdf_utils import process_pdf_from_folder
import logging
from typing import Dict, List, Any
from opensearchpy.helpers import bulk
import os
import uuid
import json
from config.experimental_config import ExperimentalConfig
from config.config import Config
from core.dynamodb import DynamoDBOperations
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def clean_text_for_vector_db(text):
    """
    Cleans the input text by removing quotes, special symbols, extra whitespaces,
    newline (\n), and tab (\t) characters.

    Args:
        text (str): The input text to clean.

    Returns:
        str: The cleaned text.
    """
    # Remove single and double quotes
    text = text.replace('"', '').replace("'", "")
    # Remove special symbols (keeping alphanumerics and spaces)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # Remove newlines and tabs
    text = text.replace('\n', ' ').replace('\t', ' ')
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    # Strip leading and trailing spaces
    return text.strip()

def chunk_embed_store(config : Config, experimentalConfig : ExperimentalConfig)-> None:
    """Main function to run the chunking and embedding pipeline."""
    experiment_dynamodb = DynamoDBOperations(region=config.aws_region, table_name=config.experiment_table)
    logger.info(experiment_dynamodb.table)
    try:
        """Main function to run the pipeline."""
        
        if not experimentalConfig.kb_data:
            raise ValueError("S3 path is missing in the kb_data field.")
        
        pdf_folder_path = S3Util().download_directory_from_s3(experimentalConfig.kb_data)
        
        # Step 1: Chunking
        chunks = ChunkingProcessor(experimentalConfig).chunk(process_pdf_from_folder(pdf_folder_path))
        
        # Step 2: Embedding
        embedding_results = EmbedProcessor(experimentalConfig).embed(chunks)
        documents = [
            {
                "_index": experimentalConfig.index_id,
                "execution_id":experimentalConfig.execution_id,
                "chunk_id": str(uuid.uuid4()),  # Generate a unique UUID for each chunk
                "text": clean_text_for_vector_db(chunk),
                config.vector_field: embedding,
                "metadata": metadata  # Optional metadata, defaulting to an empty dictionary
            }
            for embedding, chunk, metadata in embedding_results  # Enumerate is unnecessary since UUIDs are used
        ]

        total_index_embed_tokens = 0
        for _, _, metadata in embedding_results:
            total_index_embed_tokens += int(metadata['inputTokens'])

        logger.info(f"Experiment {experimentalConfig.experiment_id} Indexing Embed Tokens : {total_index_embed_tokens}")

        experiment_dynamodb.update_item(
                    key={'id': experimentalConfig.experiment_id},
                    update_expression="SET index_embed_tokens = :embed",
                    expression_values={':embed': total_index_embed_tokens}
                )
        
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
    logger.info(f"Opensearch Bulk insert initiated")
    bulk(vector_database.client, documents, chunk_size=chunk_size, max_retries=1)
    logger.info("Opensearch Bulk insert successful \n Pipeline completed successfully.")



