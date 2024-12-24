import logging
import boto3
from config.experimental_config import ExperimentalConfig
from config.config import Config, get_config

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

class DocumentReranker:
    def __init__(self):
        """
        Initialize the DocumentReranker with the AWS region, model ID, and Bedrock agent runtime.
        
        Args:
            region (str): The AWS region to use.
            model_id (str): The model ID to use for reranking.
            bedrock_agent_runtime (object): The Bedrock agent runtime instance to interact with the API.
        """
        self.region = Config.aws_region
        self.rerank_model_id = ExperimentalConfig.rerank_model_id
        self.bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=self.region)
        
    def rerank_documents(self, input_prompt, retrieved_documents):
        """
        Rerank a list of documents based on a query using Amazon Bedrock's reranking model.
        
        Args:
            input_prompt (str): The query to rerank documents for.
            retrieved_documents (list): The list of documents to be reranked.
        
        Returns:
            list: A list of reranked documents in order of relevance.
        """
        try:
            # Construct the model ARN using the provided model ID
            model_package_arn = f"arn:aws:bedrock:{self.region}::foundation-model/{self.rerank_model_id}"
            rerank_return_count = len(retrieved_documents)
            
            # Prepare the text sources for the documents (wrap text in a dictionary)
            document_sources = [{
                "type": "INLINE",
                "inlineDocumentSource": {
                    "type": "TEXT",
                    "textDocument": {
                        "text": doc['text']  # Wrap the text in a dictionary
                    }
                }
            } for doc in retrieved_documents]

            # Call the Bedrock API for reranking
            response = self.bedrock_agent_runtime.rerank(
                queries=[{
                    "type": "TEXT",
                    "textQuery": {"text": input_prompt}
                }],
                sources=document_sources,
                rerankingConfiguration={
                    "type": "BEDROCK_RERANKING_MODEL",
                    "bedrockRerankingConfiguration": {
                        "numberOfResults": rerank_return_count,
                        "modelConfiguration": {"modelArn": model_package_arn}
                    }
                }
            )

            # Check if 'results' exist in the response and log the structure
            if 'results' not in response:
                logger.error("Error in rerank response: No results found.")
                return []
            
            # Create a list to store the reranked documents
            reranked_documents = []

            # Process the results
            for rank, result in enumerate(response['results']):
                if isinstance(result, dict) and 'index' in result:
                    original_index = result['index']
                    reranked_documents.append({'text': retrieved_documents[original_index]['text']})
                else:
                    logger.error(f"Unexpected result format: {result}")

            logger.info(f"Reranked documents: {len(reranked_documents)}")
            # Return the reranked documents, ensuring we return only as many as requested
            return reranked_documents[:rerank_return_count]

        except Exception as e:
            # Catch any other unforeseen errors
            logger.error(f"An error occurred: {e}")
            return []