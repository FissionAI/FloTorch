import json
from abc import ABC, abstractmethod
import sys
from flotorch_core.logger.global_logger import get_logger

logger = get_logger()

class BaseFargateTaskProcessor(ABC):
    """
    Abstract base class for Fargate task processors.
    """

    def __init__(self, input_data: dict):
        """
        Initializes the task processor with input data.
        Args:
            input_data (dict): The input data for the task.
        """
        self.input_data = input_data

    @abstractmethod
    def process(self):
        """
        Abstract method to be implemented by subclasses for processing tasks.
        """
        raise NotImplementedError("Subclasses must implement the process method.")

    def send_task_success(self):
        """
        Sends task success signal.
        """
        print(json.dumps({"status": "success", "output": "Retrieval completed successfully"}))
        sys.exit(0)

    def send_task_failure(self, error_message: str):
        """
        Sends task failure signal.
        Args:
            error_message (str): The error message to send.
        """
        print(json.dumps({"status": "failure", "output": "Retrieval Failed", "error": error_message}))
        sys.exit(1)