import boto3
from config.config import Config
import logging
import functools

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class KnowledgeBaseUtils():
    def __init__(self, region):
        """Initialize KnowledgeBaseUtils with config and bedrock-agent client"""
        self.config = Config.load_config()
        self.client = boto3.client("bedrock-agent", region_name=region)

    def list_knowledge_bases(self):
        """
        List and filter vector knowledge bases that contain documents.
        
        Returns:
            list: List of dictionaries containing knowledge base IDs and names that:
                 - Are of type VECTOR
                 - Have at least one data source in AVAILABLE STATE
                 
        Raises:
            Exception: If there is an error listing or accessing knowledge bases
        """
        try:
            # Get list of all knowledge bases with pagination limit of 123
            response = self.client.list_knowledge_bases(maxResults=1000)
            logger.debug(f"Knowledge bases list response: {response}")
            valid_knowledge_bases = []
            # Process each knowledge base
            for item in response.get('knowledgeBaseSummaries'):
                if item.get('status') == "ACTIVE":
                
                    kb_id = item.get("knowledgeBaseId")
                    kb_name = item.get("name")
                    kb_description = item.get("description", "")
                    logger.debug(f"Processing knowledge base: {kb_name} ({kb_id})")
                    
                    # Get detailed configuration for the knowledge base
                    kb_details = self.client.get_knowledge_base(knowledgeBaseId=kb_id)
                    
                    # Only process vector type knowledge bases
                    if kb_details['knowledgeBase']['knowledgeBaseConfiguration']['type'] == "VECTOR":
                        logger.info(f"Found vector knowledge base: {kb_name} ({kb_id})")
                        
                        # List all the data source associated with the knowledge base
                        data_sources = self.client.list_data_sources(knowledgeBaseId=kb_id, maxResults=1000)
                        # Check if at least one data source is in AVAILABLE status
                        has_available_data_source = any(ds['status'] == 'AVAILABLE' for ds in data_sources['dataSourceSummaries'])
                        
                        if has_available_data_source:
                            logger.info(f"Found at least one AVAILABLE data source for knowledge base: {kb_name}")
                        
                            valid_knowledge_bases.append({
                                'kb_id': kb_id,
                                'name': kb_name,
                                'description': kb_description
                                })

                    else:
                        logger.debug(f"Skipping non-vector knowledge base: {kb_name} ({kb_id})")
                    
        except Exception as e:
            logger.error(f"Failed to list knowledge bases: {str(e)}")
            raise e
        
        return valid_knowledge_bases
    
    @functools.lru_cache(maxsize=128)
    def get_kb_name(self, kb_id):
        """Get the name of a knowledge base given its ID"""
        try:
            response = self.client.get_knowledge_base(knowledgeBaseId=kb_id)
            name = response['knowledgeBase']['name']
            return name
        except Exception as e:
            logger.error(f"Failed to get knowledge base name: {str(e)}")
            raise e
