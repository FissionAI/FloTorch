import boto3
from typing import Dict, List
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class GuardRailsUtils:
    @staticmethod
    def get_bedrock_guardrails(region) -> List[Dict]:
        "Static method to fetch AWS Bedrock guardrails."

        try:
            client = boto3.client('bedrock', region_name=region)

            logger.info("Fetching guardrails.")            
            response = client.list_guardrails()
            guardrails = response.get("guardrails", [])
            logger.info("Guardrails fetched.")

            all_guardrails = []

            for guardrail in guardrails:
                guardrail_id = guardrail.get("id")
                
                # Fetch all versions for this guardrail
                logger.info(f"Fetching versions for guardrail: {guardrail_id}")
                versions_response = client.list_guardrails(
                    guardrailIdentifier=guardrail_id
                )
                versions = versions_response.get("guardrails", [])
                
                # Handle pagination for versions
                next_token = versions_response.get("nextToken")
                while next_token:
                    versions_response = client.list_guardrails(
                        guardrailIdentifier=guardrail_id,
                        nextToken=next_token
                    )
                    versions.extend(versions_response.get("guardrails", []))
                    next_token = versions_response.get("nextToken")
                
                # Add each version as a separate entry
                for version in versions:
                    all_guardrails.append({
                        "guardrails_id": version.get("id"),
                        "description": version.get("description"),
                        "name": version.get("name"),
                        "version": version.get("version"),
                        "arn": version.get("arn")
                    })
            
            logger.info(f"Successfully fetched {len(all_guardrails)} guardrail versions.")
            return all_guardrails
            
        except Exception as e:
            logger.error(f"Failed to fetch guardrails: {str(e)}")
            raise Exception(f"Failed to fetch guardrails: {str(e)}")
        
