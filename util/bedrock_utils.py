import boto3
from config.config import Config
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class KnowledgeBaseUtils():
    def __init__(self):
        """Initialize KnowledgeBaseUtils with config and bedrock-agent client"""
        self.config = Config.load_config()
        self.client = boto3.client("bedrock-agent", region_name=self.config.aws_region)

    def list_knowledge_bases(self):
        """
        List and filter vector knowledge bases that contain documents.
        
        Returns:
            list: List of dictionaries containing knowledge base IDs and names that:
                 - Are of type VECTOR
                 - Have at least one data source with documents
                 
        Raises:
            Exception: If there is an error listing or accessing knowledge bases
        """
        try:
            # Get list of all knowledge bases with pagination limit of 123
            response = self.client.list_knowledge_bases(maxResults=1000)
            valid_knowledge_bases = []
            print(response)
            # Process each knowledge base
            for item in response.get('knowledgeBaseSummaries'): 
                kb_id = item.get("knowledgeBaseId")
                kb_name = item.get("name")
                kb_description = item.get("description", "")
                logger.debug(f"Processing knowledge base: {kb_name} ({kb_id})")
                
                # Get detailed configuration for the knowledge base
                kb_details = self.client.get_knowledge_base(knowledgeBaseId=kb_id)
                
                # Only process vector type knowledge bases
                if kb_details['knowledgeBase']['knowledgeBaseConfiguration']['type'] == "VECTOR":
                    logger.info(f"Found vector knowledge base: {kb_name} ({kb_id})")
                    
                    # Get the first data source ID for the knowledge base
                    data_sources = self.client.list_data_sources(knowledgeBaseId=kb_id, maxResults=1000)
                    data_source_id = data_sources['dataSourceSummaries'][0]['dataSourceId']
                    logger.debug(f"Found data source: {data_source_id} for knowledge base: {kb_name}")
                    
                    # Check if data source contains any documents
                    files = self.client.list_knowledge_base_documents(knowledgeBaseId=kb_id, 
                                                                      dataSourceId=data_source_id,
                                                                      maxResults=1000
                                                                        )
                    if len(files['documentDetails']) > 0:
                        logger.info(f"Found {len(files['documentDetails'])} documents in knowledge base: {kb_name}")
                    
                        valid_knowledge_bases.append({
                            'kb_id': kb_id,
                            'name': kb_name,
                            'description': kb_description
                            })
                        
                    else:
                        logger.warning(
                            f"No documents found in knowledge base: {kb_name}. "
                            "Add files to the data source or sync the data source if files were already added."
                        )
                    
                else:
                    logger.debug(f"Skipping non-vector knowledge base: {kb_name} ({kb_id})")
                    
        except Exception as e:
            logger.error(f"Failed to list knowledge bases: {str(e)}")
            raise e
        
        return valid_knowledge_bases