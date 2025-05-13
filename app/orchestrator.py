import json
import boto3
from decimal import Decimal
from fastapi import HTTPException
import os
from config.config import get_config
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StepFunctionOrchestrator:
    """
    Handles Step Function orchestration for experiment execution.
    """
    def __init__(self):
        self.config = get_config()
        self.step_function_client = self._initialize_step_function_client()

    def _initialize_step_function_client(self) -> boto3.client:
        """
        Initialize the AWS Step Function client.

        Returns:
            boto3.client: Configured Step Function client
        """
        try:
            return boto3.client("stepfunctions", region_name=self.config.aws_region)
        except Exception as e:
            logger.error(f"Failed to initialize Step Function client: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to initialize AWS Step Function client"
            )

    def _prepare_execution_payload(self, execution_id: str) -> str:
        """
        Prepare the payload for Step Function execution.

        Args:
            execution_id (str): The execution ID

        Returns:
            str: JSON string payload
        """
        try:
            payload = {"execution_id": execution_id}
            return json.dumps(payload)
        except Exception as e:
            logger.error(f"Failed to prepare execution payload: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to prepare execution payload"
            )

    def run_experiment_orchestration(self, execution_id: str) -> Dict[str, Any]:
        """
        Trigger the invocation of step function for execution.

        Args:
            execution_id (str): The execution ID.

        Returns:
            Dict[str, Any]: Response from Step Function execution

        Raises:
            HTTPException: If orchestration fails
        """
        try:
            # Prepare the payload
            payload = self._prepare_execution_payload(execution_id)

            # Start the Step Function execution
            response = self.step_function_client.start_execution(
                stateMachineArn=self.config.step_function_arn,
                input=payload
            )

            logger.info(f"Started Step Function with Execution ARN: {response['executionArn']}")
            return response

        except Exception as e:
            error_message = f"Failed to execute orchestration: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise HTTPException(status_code=500, detail=error_message)

# Create a singleton instance
orchestrator = StepFunctionOrchestrator()

def run_experiment_orchestration(execution_id: str) -> Dict[str, Any]:
    """
    Wrapper function for backward compatibility.

    Args:
        execution_id (str): The execution ID.

    Returns:
        Dict[str, Any]: Response from Step Function execution
    """
    return orchestrator.run_experiment_orchestration(execution_id)
