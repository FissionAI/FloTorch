import boto3
from typing import Dict, List, Tuple, Any
from baseclasses.base_classes import BaseEmbedder
from util.boto3_utils import BedRockRetryHander
import json

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Bedrock Base Embedder
class BedrockEmbedder(BaseEmbedder):
    def __init__(self, model_id: str, region: str, role_arn: str = None) -> None:
        super().__init__(model_id)
        self.client = boto3.client("bedrock-runtime", region_name=region)

    def prepare_payload(self, text: str, dimensions: int, normalize: bool) -> Dict:
        raise NotImplementedError("Subclasses must implement `prepare_payload`")

    @BedRockRetryHander()
    def embed(self, text: str, dimensions: int = 256, normalize: bool = True) -> Tuple[Dict[Any, Any], List[float]]:
        try:
            payload = self.prepare_payload(text, dimensions, normalize)
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload)
            )
            model_response = json.loads(response["body"].read())
            metadata = {}
            if response and 'ResponseMetadata' in response and 'HTTPHeaders' in response['ResponseMetadata']:
                input_tokens = response['ResponseMetadata']['HTTPHeaders']['x-amzn-bedrock-input-token-count']
                latency = response['ResponseMetadata']['HTTPHeaders']['x-amzn-bedrock-invocation-latency']
                metadata = {
                    'inputTokens': input_tokens,
                    'latencyMs': latency
                }
            return metadata, self.extract_embedding(model_response)
        except Exception as e:
            logger.error(f"Error during embedding: {e}")
            raise

    def extract_embedding(self, response: Dict) -> List[float]:
        raise NotImplementedError("Subclasses must implement `extract_embedding`")