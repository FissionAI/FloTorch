import boto3
from typing import Dict, List
from botocore.exceptions import ClientError
from baseclasses.base_classes import BaseEmbedder
from sagemaker.session import Session
from sagemaker.predictor import Predictor
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer
from sagemaker.jumpstart.model import JumpStartModel
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri
import sagemaker
import logging
import numpy as np
import json
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Model configurations
EMBEDDING_MODELS = {
    "huggingface-sentencesimilarity-bge-large-en-v1-5": {
        "model_name": "bge-large",
        "model_source": "jumpstart",
        "dimension": 1024,
        "instance_type": "ml.g5.2xlarge",
        "input_key": "text_inputs"
    },
    "huggingface-sentencesimilarity-bge-m3": {
        "model_name": "bge-m3",
        "model_source": "jumpstart",
        "dimension": 1024,
        "instance_type": "ml.g5.2xlarge",
        "input_key": "text_inputs"
    },
    "huggingface-textembedding-gte-qwen2-7b-instruct": {
        "model_name": "qwen",
        "model_source": "jumpstart",
        "dimension": 3584,
        "instance_type": "ml.g5.2xlarge",
        "input_key": "inputs"
    }
}

# Sagemaker Base Embedder
class SageMakerEmbedder(BaseEmbedder):
    def __init__(self, model_id: str, region: str, role_arn: str) -> None:
        """
        Initializes the SageMakerEmbedder with the given model ID, region, and role ARN.
        Sets up necessary SageMaker runtime clients, session, and endpoint predictor.

        Args:
            model_id (str): The unique identifier for the model.
            region (str): The AWS region where the SageMaker services are hosted.
            role_arn (str): The ARN of the IAM role. Currently not used but included for future extensions.
        """

        # Initialize the base class
        super().__init__(model_id)
        
        # Store the region
        self.region_name = region
        
        self.role = role_arn
        
        # Initialize the SageMaker runtime and client for general operations
        self.client = boto3.client("sagemaker-runtime", region_name=region)
        self.sagemaker_client = boto3.client('sagemaker', region_name=region)
        
        # Create a new SageMaker session
        self.session = Session(boto_session=boto3.Session(region_name=region))
        
        # Initialize additional embedding-related attributes
        self.embedding_model_id = model_id
        # self.embedding_model_endpoint_name = 'flotorch-embedding-endpoint'
        self.embedding_model_endpoint_name = f"{self._sanitize_name(model_id)[:44]}-embedding-endpoint"
        
        self.embedding_dimension = EMBEDDING_MODELS.get(model_id, {}).get('dimension', 1024)
        
        self.wait_time = 5
        
        # Ensure the endpoint exists or create it if necessary
        self._ensure_endpoint_exists()
        
        # Initialize the predictor to interact with the SageMaker endpoint
        self.predictor = Predictor(
            endpoint_name=self.embedding_model_endpoint_name,
            sagemaker_session=self.session
        )
        
        # Set up the serializer and deserializer for the predictor
        self.predictor.serializer = JSONSerializer()
        self.predictor.deserializer = JSONDeserializer()

        self.embedding_predictor = self.predictor
        
        # Log initialization success
        logger.info(f"Initialized SageMakerEmbedder for model {model_id} in region {region}.")

    def _ensure_endpoint_exists(self):
        """
        Ensures that the SageMaker endpoint exists for the given model. If the endpoint does not exist,
        it creates a new endpoint using the specified model ID.

        Args:
            model_id (str): The unique identifier for the model to use for the endpoint.

        Raises:
            ClientError: If there is an issue communicating with SageMaker or creating the endpoint.
        """
        
        try:
            # Check if the endpoint already exists
            _ = self._check_model_status(self.embedding_model_endpoint_name)
            logger.info(f"Endpoint {self.embedding_model_endpoint_name} already exists.")
        except self.sagemaker_client.exceptions.ClientError:
            # If the endpoint does not exist, create a new one
            logger.info(f"Endpoint and configuration for {self.embedding_model_endpoint_name} does not exist. Creating endpoint.")
            self.create_endpoint(endpoint_name=self.embedding_model_endpoint_name, model_id=self.embedding_model_id)
            
    def _check_model_status(self, endpoint_name):
        """
        Check the status of the SageMaker endpoint and its configuration.
        
        This method performs the following:
        1. Checks if endpoint exists and is in service
        2. If endpoint is being created, waits until creation completes
        3. If no endpoint exists, checks for endpoint configuration
        4. If configuration exists, waits for endpoint creation to complete
        
        Args:
            endpoint_name (str): Name of the SageMaker endpoint to check
            
        Returns:
            str: 'InService' if endpoint is available and running
            
        Raises:
            Exception: If endpoint creation fails or has unexpected status
            ClientError: If neither endpoint nor configuration exists
        """
        try:
            while True: 
                # Poll endpoint status until it is in service or fails
                response = self.sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
                
                if response['EndpointStatus'] == 'InService':
                    logger.info(f"Endpoint {endpoint_name} is in service.")
                    return 'InService'
                
                elif response['EndpointStatus'] == 'Failed':
                    logger.error(f"Endpoint {endpoint_name} creation failed.")
                    raise Exception(f"Endpoint {endpoint_name} creation failed.")
                
                elif response['EndpointStatus'] == 'Creating':
                    time.sleep(self.wait_time) # Pause before next status check
                    
                else:
                    raise Exception(f"Unexpected endpoint status: {response['EndpointStatus']}")
                
        except self.sagemaker_client.exceptions.ClientError: 
            # No endpoint exists - check if there's a configuration waiting to be deployed
            logger.info(f"Endpoint {endpoint_name} does not exist. Checking if endpoint configuration exists.")
            
            try: 
                # Look for endpoint configuration that may have been created by another process
                response = self.sagemaker_client.describe_endpoint_config(EndpointConfigName=endpoint_name)
                logger.info(f"Configuration for {endpoint_name} exists, waiting {self.wait_time} seconds for endpoint creation.")
                
                time.sleep(self.wait_time) # Allow time for endpoint creation to begin
                
                _ = self._check_model_status(endpoint_name)  # Keep rechecking the endpoint status until it begins creation
                
            except self.sagemaker_client.exceptions.ClientError: 
                # Neither endpoint nor configuration exists
                logger.info(f"Endpoint configuration does not exist.")
                raise
            
        except Exception as e:
            logger.error(f"Error checking endpoint status: {e}")
            raise

    def create_endpoint(self, endpoint_name: str, model_id: str) -> sagemaker.predictor.Predictor:
        """
        Creates a SageMaker endpoint for the specified model if it doesn't already exist.
        If the endpoint is already in service, returns the existing predictor.
        
        Args:
            endpoint_name (str): The name of the SageMaker endpoint to be created or fetched.
            model_id (str): The identifier for the model to be used in the endpoint.
        
        Returns:
            sagemaker.predictor.Predictor: A predictor object for the created or fetched endpoint.

        Raises:
            ValueError: If the provided model_id is not supported.
            ClientError: If there are AWS API errors during endpoint creation/access.
        """
        
        # Validate that model_id exists in our supported model configurations
        if model_id not in EMBEDDING_MODELS:
            raise ValueError(f"Unsupported model ID: {model_id}")

        # Create AWS and SageMaker sessions for API interactions
        boto_session = boto3.Session(region_name=self.region_name)
        sagemaker_session = sagemaker.Session(boto_session=boto_session)

        # Look up the appropriate instance type from model configurations
        instance_type = (EMBEDDING_MODELS.get(model_id))['instance_type']
        model_source = (EMBEDDING_MODELS.get(model_id))['model_source']
        
        try:
            # First check if a working endpoint already exists to avoid duplicate creation
            status = self._check_model_status(endpoint_name)
            if status == 'InService':
                # Endpoint exists and is healthy - create and return a predictor for it
                predictor = sagemaker.predictor.Predictor(
                    endpoint_name=endpoint_name,
                    sagemaker_session=sagemaker_session,
                    serializer=sagemaker.serializers.JSONSerializer(),
                    deserializer=sagemaker.deserializers.JSONDeserializer()
                )
                # Register the predictor with the appropriate model type handler
                self._assign_predictor(predictor, model_id)
                return predictor
                
        except self.sagemaker_client.exceptions.ClientError as e:
            # Handle case where endpoint doesn't exist yet
            if e.response['Error']['Code'] == 'ValidationException':
                try:
                    if model_source == "jumpstart":
                        # Initialize a new JumpStart model with the specified configuration
                        model = JumpStartModel(
                            role = self.role,
                            model_id=model_id,
                            sagemaker_session=sagemaker_session
                        )
                        
                        # Deploy the model to a new endpoint with the specified configuration
                        predictor = model.deploy(
                            initial_instance_count=1,
                            instance_type=instance_type,
                            endpoint_name=endpoint_name,
                            accept_eula=True  # Required for JumpStart models
                        )
                    # Check if the model source is huggingface    
                    elif model_source == "huggingface":
                        hub = {
                            'HF_MODEL_ID': model_id,
                            'SM_NUM_GPUS': json.dumps(1)
                        }
                        huggingface_model = HuggingFaceModel(
                            image_uri=get_huggingface_llm_image_uri("huggingface", version="2.3.1", region=self.region_name),
                            env=hub,
                            role=self.role, 
                        )

                        # deploy model to SageMaker Inference
                        predictor = huggingface_model.deploy(
                            initial_instance_count=1,
                            instance_type=instance_type,
                            endpoint_name=endpoint_name,
                            container_startup_health_check_timeout=300,
                        )
                    
                    # Register the new predictor with the appropriate model type handler
                    self._assign_predictor(predictor, model_id)
                    return predictor
                
                except self.sagemaker_client.exceptions.ClientError as e:
                    # Handle race condition where another process started creating the endpoint
                    # between our existence check and creation attempt
                    logger.info(f"Error creating endpoint: {e}")
                    if e.response['Error']['Code'] == 'ValidationException':
                        
                        logger.info(f"A new endpoint creation intercepted while attempting to create new endpoint, waiting.")
                        time.sleep(self.wait_time) # Allow the other process's endpoint to finish creating
                        
                        status = self._check_model_status(endpoint_name)
                        
                        if status == 'InService':
                            logger.info(f"Found the new endpoint, creating the predictor.")
                            # Create predictor for the endpoint that the other process created
                            predictor = sagemaker.predictor.Predictor(
                                endpoint_name=endpoint_name,
                                sagemaker_session=sagemaker_session,
                                serializer=sagemaker.serializers.JSONSerializer(),
                                deserializer=sagemaker.deserializers.JSONDeserializer()
                            )
                            
                            # Register with appropriate model type handler
                            self._assign_predictor(predictor, model_id)
                            
                            return predictor
                        
                    elif e.response['Error']['Code'] == 'ResourceLimitExceeded':
                        logger.error(f"Resource limit exceeded while creating endpoint: {e}")
                        raise
            
            # Re-raise any unexpected AWS API errors
            raise

    def _assign_predictor(self, predictor: sagemaker.predictor.Predictor, model_id: str):
        """
        Assigns the appropriate predictor based on the provided model_id. The predictor is assigned to either 
        the embedding or inferencing predictor attributes, depending on the model type.

        Args:
            predictor (sagemaker.predictor.Predictor): The SageMaker predictor to be assigned.
            model_id (str): The model ID which determines whether the predictor is for embedding or inferencing.
        
        """
        # Assign predictor for embedding models
        if model_id in EMBEDDING_MODELS:
            self.embedding_predictor = predictor
            self.embedding_dimension = EMBEDDING_MODELS[model_id]['dimension']
            self.embedding_model_id = model_id
            logger.info(f"Assigned embedding predictor for model: {model_id}")
        
        # Log an error if the model_id doesn't match any known type
        else:
            logger.error(f"Model ID {model_id} is not recognized as an embedding model.")

    def embed(self, text: str, dimensions: int = 256, normalize: bool = True) -> List[float]:
        """
        Retrieves the embedding for the given input text from the model's predictor.

        Args:
            text (str): The input text for which the embedding is generated.

        Returns:
            List[float]: The generated embedding as a list of floats.

        Raises:
            ValueError: If the predictor is not initialized or if the input text is empty.
            Exception: If there is an error during the embedding extraction process.
        """

        # Validate predictor initialization
        if not self.predictor:
            raise ValueError("Embedding predictor not initialized")

        # Ensure the input text is not empty
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")

        try:
            # # Prepare the input payload for prediction
            # input_data = {
            #     "text_inputs": [text],
            #     "mode": "embedding"  # Define the mode to request embedding
            # }

            input_data = self.prepare_payload(text)
            
            # Log the prediction details
            logger.debug("Input data prepared for prediction: %s", json.dumps(input_data, indent=2))
            logger.debug("Using model ID: %s", self.embedding_model_id)

            # SageMaker does not provide input tokens as metadata.
            # As a workaround, we use a rough approximation: ~4 characters per token.
            input_tokens = len(text) // 4
            
            start_time = time.time()
            
            # Make the prediction request
            response = self.embedding_predictor.predict(input_data)

            # Calculate latency metrics
            latency = int((time.time() - start_time) * 1000)
            
            # If the response is in byte format, decode it
            if isinstance(response, (bytes, bytearray)):
                response = json.loads(response.decode('utf-8'))
            elif isinstance(response, str):
                response = json.loads(response)

            # Extract the embedding from the response
            if isinstance(response, dict) and 'embedding' in response:
                embedding = np.array(response['embedding'][0] if isinstance(response['embedding'], list) else response['embedding'])
            else:
                embedding = np.array(response[0] if isinstance(response, list) else response)

            # Flatten the embedding to ensure it's a 1D array
            embedding = embedding.flatten()

            # Normalize the embedding to unit length
            embedding = embedding / np.linalg.norm(embedding)

            # Check if the embedding dimension matches the expected value (1024)
            if len(embedding) != self.embedding_dimension:
                logger.warning(f"Embedding dimension mismatch. Expected 1024, got {len(embedding)}")
                # Adjust the dimension by truncating or padding
                if len(embedding) > self.embedding_dimension:
                    embedding = embedding[:self.embedding_dimension]
                else:
                    embedding = np.pad(embedding, (0, self.embedding_dimension - len(embedding)))

            metadata = {
                    'inputTokens': input_tokens,
                    'latencyMs': latency
                }
            # Return the embedding as a list of floats
            return metadata, embedding.tolist()

        except Exception as e:
            # Log detailed error information for debugging
            logger.error("Error in get_embedding: %s", str(e))
            logger.error("Model ID: %s", self.embedding_model_id)
            logger.error("Input text length: %d", len(text))
            logger.error("Input data: %s", json.dumps(input_data, indent=2))

            # Log the response structure if available
            if 'response' in locals():
                logger.error("Response structure: %s", type(response))
                try:
                    logger.error("Response content: %s", json.dumps(response, indent=2))
                except Exception as json_error:
                    logger.error("Response content (raw): %s", response)

            # Re-raise the exception after logging
            raise
    
    def prepare_payload1(self, text: str, dimensions: int, normalize: bool) -> Dict:
        raise NotImplementedError("Subclasses must implement `prepare_payload`")
    
    def prepare_payload(self, text: str) -> Dict:
        """
        Prepares the payload for the embedding model based on the provided text.

        Args:
            text (str): The input text to be processed by the model.

        Raises:
            ValueError: If the embedding model ID is unknown.

        Returns:
            Dict: The payload containing the appropriate input and model configurations.
        """
        
        # Retrieve model configuration based on model ID
        model_config = EMBEDDING_MODELS.get(self.embedding_model_id)
        if not model_config:
            raise ValueError(f"Unknown model ID: {self.embedding_model_id}")
            
        # Extract the input key from the model configuration
        input_key = model_config["input_key"]
        
        # Build the payload with the input text
        payload = {
            input_key: [text]
        }
        
        # Add mode only for models that need it
        if self.embedding_model_id != "huggingface-textembedding-gte-qwen2-7b-instruct":
            payload["mode"] = "embedding"
                
        return payload
    
    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Sanitize the endpoint name to follow AWS naming conventions"""
        # Replace any character that's not alphanumeric or hyphen with hyphen
        import re
        name = re.sub(r'[^a-zA-Z0-9-]', '-', name)
        # Ensure it starts with a letter
        if not name[0].isalpha(): 
            name = 'n' + name
        # Truncate to 63 characters (AWS limit)
        return name[:63]