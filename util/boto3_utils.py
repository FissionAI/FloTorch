from typing import Dict
import time 
import logging
import botocore

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def bedrock_retry_handler(func):
    def wrapper(*args, **kwargs):
        MAX_RETRIES = 5
        RETRY_DELAY = 2
        BACKOFF_FACTOR = 2
        
        retries = 0
        while retries < MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except botocore.exceptions.ClientError as e:
                error_code = e.response['Error']['Code']
                RETRYABLE_ERRORS = {'ThrottlingException', 'RequestLimitExceeded'}
                if error_code in RETRYABLE_ERRORS: # Add more exceptions if required
                    retries += 1
                    logger.error(f"Rate limit error in Bedrock converse (Attempt {retries}/{MAX_RETRIES}): {str(e)}")
                    
                    if retries >= MAX_RETRIES:
                        logger.error("Max retries reached. Could not complete Bedrock converse operation.")
                        raise
                    
                    backoff_time = RETRY_DELAY * (BACKOFF_FACTOR ** (retries - 1))
                    logger.info(f"Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
                else:
                    # If it's not a rate limit error, raise immediately
                    raise
            except Exception as e:
                # For any other exception, log and raise immediately
                logger.error(f"Unexpected error in Bedrock converse: {str(e)}")
                raise
        
    return wrapper