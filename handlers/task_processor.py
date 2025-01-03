import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


class FargateTaskProcessor():
    def __init__(self):
        self.sfn_client = boto3.client('stepfunctions')
        self.task_token = os.environ.get('TASK_TOKEN')
        event_data = os.environ.get('INPUT_DATA', '{}')
        if isinstance(event_data, str):
            self.input_data = json.loads(event_data)
        else:
            self.input_data = event_data
        logger.info(f"Input data: {self.input_data}")

    def process(self):
        raise NotImplementedError("Subclasses must implement the process method.")

    def send_task_success(self, output):
        try:
            self.sfn_client.send_task_success(
                taskToken=self.task_token,
                output=json.dumps(output)
            )
        except ClientError as e:
            logger.error(f"Error sending task success: {str(e)}")
            raise

    def send_task_failure(self, error):
        try:
            self.sfn_client.send_task_failure(
                taskToken=self.task_token,
                error='TaskProcessingError',
                cause=error.get('errorMessage')
            )
        except ClientError as e:
            logger.error(f"Error sending task failure: {str(e)}")
            raise
