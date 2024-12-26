from typing import Dict
import time 
import logging
import botocore
from baseclasses.base_classes import BotoRetryHandler, RetryParams

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

class BedRockRetryHander(BotoRetryHandler):
    """Retry handler for Bedrock service."""
    @property
    def retry_params(self) -> RetryParams:
        return RetryParams(
            max_retries=5,
            retry_delay=2,
            backoff_factor=2
        )
    
    @property
    def retryable_errors(self):
        return {
            "ThrottlingException",
            "ServiceQuotaExceededException",
            "ModelTimeoutException"
        }