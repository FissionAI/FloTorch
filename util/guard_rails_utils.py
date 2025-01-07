import boto3
from typing import Dict
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class GuardRailsUtils:
    @staticmethod
    def get_bedrock_guardrails() -> Dict:
        "Static method to fetch AWS Bedrock guardrails."

        try:
            client = boto3.client('bedrock')

            logger.info("Fetching guardrails.")            
            response = client.list_guardrails()
            guardrails = response.get("guardrails", [])
            logger.info("Guardrails fetched.")
            
            return [
                    {
                        "guardrails_id": guardrail.get("id"), 
                        "description": guardrail.get("description"), 
                        "name": guardrail.get("name"),
                        "version": guardrail.get("version")
                    }
                    for guardrail in guardrails
                ]
        except Exception as e:
            logger.error(f"Failed to fetch guardrails: {str(e)}")
            raise Exception(f"Failed to fetch guardrails: {str(e)}")