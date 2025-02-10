import boto3
from typing import List, Dict
from botocore.exceptions import ClientError
from baseclasses.base_classes import BaseInferencer
from config.experimental_config import ExperimentalConfig
from sagemaker.session import Session
from sagemaker.predictor import Predictor
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer
from sagemaker.jumpstart.model import JumpStartModel
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri
import sagemaker
import logging
import time
import random
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Model configurations

INFERENCER_MODELS = {
    "meta-textgeneration-llama-3-1-8b-instruct": {
        "model_source": "jumpstart",
        "instance_type": "ml.g5.2xlarge"
    },
    "huggingface-llm-falcon-7b-instruct-bf16": {
        "model_source": "jumpstart",
        "instance_type": "ml.g5.2xlarge"
    },
    "meta-textgeneration-llama-3-3-70b-instruct": {
        "model_source": "jumpstart",
        "instance_type": "ml.p4d.24xlarge"
    }
    ,
    "deepseek-ai/DeepSeek-R1-Distill-Llama-8B": {
        "model_source": "huggingface",
        "instance_type": "ml.g5.2xlarge"
    }
    ,
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B": {
        "model_source": "huggingface",
        "instance_type": "ml.g5.2xlarge"
    }
    ,
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B": {
        "model_source": "huggingface",
        "instance_type": "ml.g5.2xlarge"
    }
    ,
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B": {
        "model_source": "huggingface",
        "instance_type": "ml.g6e.12xlarge"
    }
}

# Sagemaker Base Inferencer
class SageMakerInferencer(BaseInferencer):
    
    def __init__(self, model_id: str, experiment_config: ExperimentalConfig, region: str, role_arn: str):
        """
        Initializes the SageMakerInferencer with the given model ID, region, and role ARN.
        Sets up necessary SageMaker runtime clients, session, and endpoint predictor.

        Args:
            model_id (str): The unique identifier for the model.
            region (str): The AWS region where the SageMaker services are hosted.
            role_arn (str): The ARN of the IAM role. Currently not used but included for future extensions.
        """
        
        # Store the region
        self.region_name = region
        
        self.role = role_arn
        
        # Initialize the base class
        super().__init__(model_id, experiment_config, region, role_arn)

        logger.info(f"Initializing SageMaker Generator for model: {model_id}")

        # Initialize the SageMaker runtime and client for general operations
        self.client = boto3.client("sagemaker-runtime", region_name=region)
        self.sagemaker_client = boto3.client('sagemaker', region_name=region)
        
        # Create a new SageMaker session
        self.session = Session(boto_session=boto3.Session(region_name=region))

        # Initialize additional inferencing-related attributes
        self.inferencing_model_id = model_id
        self.inferencing_model_endpoint_name = f"{self._sanitize_name(model_id)[:42]}-inferencing-endpoint"

        self.wait_time = 5
        
        # Ensure the endpoint exists or create it if necessary
        self._ensure_endpoint_exists()

        # Initialize the predictor to interact with the SageMaker endpoint
        self.predictor = Predictor(
            endpoint_name=self.inferencing_model_endpoint_name,
            sagemaker_session=self.session
        )

        # Set up the serializer and deserializer for the predictor
        self.predictor.serializer = JSONSerializer()
        self.predictor.deserializer = JSONDeserializer()

        self.inferencing_predictor = self.predictor
        
        # Log initialization success
        logger.info(f"Initialized SageMakerInferencer for model {model_id} in region {region}.")

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
            _ = self._check_model_status(self.inferencing_model_endpoint_name)
            logger.info(f"Endpoint {self.inferencing_model_endpoint_name} already exists.")
        except self.sagemaker_client.exceptions.ClientError:
            # If the endpoint does not exist, create a new one
            logger.info(f"Endpoint and configuration for {self.inferencing_model_endpoint_name} does not exist. Creating endpoint.")
            self.create_endpoint(endpoint_name=self.inferencing_model_endpoint_name, model_id=self.inferencing_model_id)
            
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
                
                _ = self._check_model_status(endpoint_name) # Keep rechecking the endpoint status until it begins creation
                
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
        if model_id not in INFERENCER_MODELS:
            raise ValueError(f"Unsupported model ID: {model_id}")

        # Look up the appropriate instance type from model configurations
        instance_type = INFERENCER_MODELS.get(model_id)['instance_type']
        model_source = INFERENCER_MODELS.get(model_id)['model_source']
        
        try:
            # First check if a working endpoint already exists to avoid duplicate creation
            status = self._check_model_status(endpoint_name)
            if status == 'InService':
                # Endpoint exists and is healthy - create and return a predictor for it
                predictor = sagemaker.predictor.Predictor(
                    endpoint_name=endpoint_name,
                    sagemaker_session=self.session,
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
                            sagemaker_session=self.session
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
                            sagemaker_session = self.session
                            
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
                                sagemaker_session=self.session,
                                serializer=sagemaker.serializers.JSONSerializer(),
                                deserializer=sagemaker.deserializers.JSONDeserializer()
                            )
                            
                            # Register with appropriate model type handler
                            self._assign_predictor(predictor, model_id)
                            
                            return predictor
                        
                    elif e.response['Error']['Code'] == 'ResourceLimitExceeded':
                        logger.error(f"Resource limit exceeded while creating endpoint: {e}")
                        raise
            
            # Reraise any unexpected client errors
            raise

    def _assign_predictor(self, predictor: sagemaker.predictor.Predictor, model_id: str):
        """
        Assigns the appropriate predictor based on the provided model_id. The predictor is assigned to either 
        the embedding or inferencing predictor attributes, depending on the model type.

        Args:
            predictor (sagemaker.predictor.Predictor): The SageMaker predictor to be assigned.
            model_id (str): The model ID which determines whether the predictor is for embedding or inferencing.
        
        """
        # Assign predictor for inferencing models
        if model_id in INFERENCER_MODELS:
            self.inferencing_predictor = predictor
            self.inferencing_model_id = model_id
            logger.info(f"Assigned inferencing predictor for model: {model_id}")
        
        # Log an error if the model_id doesn't match any known type
        else:
            logger.error(f"Model ID {model_id} is not recognized as an inferencing model.")
            
    def generate_prompt(self, experiment_config: ExperimentalConfig, default_prompt: str, user_query: str, context: List[Dict] = None):
        n_shot_prompt_guide = experiment_config.n_shot_prompt_guide_obj
        n_shot_prompt = experiment_config.n_shot_prompts
        # Input validation
        if n_shot_prompt < 0:
            raise ValueError("n_shot_prompt must be non-negative")
        
        # Get system prompt
        system_prompt = default_prompt if n_shot_prompt_guide is None or n_shot_prompt_guide.system_prompt is None else n_shot_prompt_guide.system_prompt
        
        context_text = ""
        if context:
            context_text = self._format_context(user_query, context)
        
        base_prompt = n_shot_prompt_guide.user_prompt if n_shot_prompt_guide.user_prompt else ""
        
        if n_shot_prompt == 0:
            logger.info("into zero shot prompt")
        
            if self.inferencing_model_id == "huggingface-llm-falcon-7b-instruct-bf16":
                prompt = f"""Below are search results and a query. Create a concise summary.
                    Query: {user_query}
                    Search Results: {context_text}
                    Summary:"""
                return prompt
                    
            else:
                prompt = (
                    "Human: " + system_prompt + "\n\n" + 
                    context_text + "\n\n" + 
                    base_prompt + "\n\n" +
                    "Assistant: The final answer is:" 
                )
                return prompt.strip()
                
        
        # Get examples
        examples = n_shot_prompt_guide.examples
        
        # Format examples
        selected_examples = (random.sample(examples, n_shot_prompt) 
                        if len(examples) > n_shot_prompt 
                        else examples)
        
        # Use string concatenation for example formatting
        example_text = ""
        for example in selected_examples:
            example_text += "- " + example["example"] + "\n"
        
        logger.info(f"into {n_shot_prompt} shot prompt  with examples {len(selected_examples)}")
        
        if self.inferencing_model_id == "huggingface-llm-falcon-7b-instruct-bf16":
            prompt = f"""Below are search results and a query. Create a concise summary.
                Query: {user_query}
                Few examples:\n 
                {example_text}\n 
                Search Results: {context_text}
                Summary:"""
                
            return prompt
        
        else:            
            prompt = (
                "Human: " + system_prompt + "\n\n" + 
                "Few examples:\n" + 
                example_text + "\n" + 
                context_text + "\n\n" + 
                base_prompt + "\n\n" +
                "Assistant: The final answer is:" 
            )
            
            return prompt.strip()
    
    def _format_context(self, user_query: str, context: List[Dict[str, str]]) -> str:
        """Format context documents into a single string."""
        # Format context: create a string representation of the query and passages
        formatted_context = f"Search Query: {user_query}\n\nRelevant Passages:\n"
        
        try:
            for i, item in enumerate(context, 1):
                # Retrieve text from the context, handling both possible structures
                content = None
                if 'text' in item:
                    content = item['text']
                elif '_source' in item and 'text' in item['_source']:
                    content = item['_source']['text']
                
                # If no text found, skip the current context item
                if not content:
                    continue
                
                # Add score to context if available
                score = item.get('_score', 'N/A')
                formatted_context += f"\nPassage {i} (Score: {score}):\n{content}\n"
            return formatted_context
        
        except Exception as e:
            logger.error(f"Error formatting context: {str(e)}")
            formatted_context += "Error processing context"
            return formatted_context
        

    def generate_text(self, user_query: str, default_prompt: str, context: List[Dict] = None, **kwargs) -> str:
        """
        Generates a response based on the provided user query and context. It formats the context, sends it to 
        the model for text generation, and processes the response to return the generated text.

        Args:
            user_query (str): The query provided by the user for which a response is generated.
            context (List[Dict]): A list of context passages, each represented as a dictionary.
            default_prompt (str): A default prompt that is used to guide the text generation.
            **kwargs: Additional keyword arguments, if any.

        Returns:
            tuple: A tuple containing metadata (str) and the cleaned generated text (str).
        """
        
        # Ensure the generation predictor is initialized
        if not self.inferencing_predictor:
            raise ValueError("Generation predictor not initialized")
        
        prompt = self.generate_prompt(self.experiment_config, default_prompt, user_query, context)
        
        # Define default parameters for the model's generation
        default_params = {
            "max_new_tokens": 256,
            "temperature": self.experiment_config.temp_retrieval_llm,
            "top_p": 0.9,
            "do_sample": True
        }
        
        # Prepare payload for model inference
        payload = {
            "inputs": prompt,
            "parameters": default_params
        }

        try:
            start_time = time.time()
            
            # Get response from the model
            response = self.inferencing_predictor.predict(payload)

            # Calculate latency metrics
            latency = int((time.time() - start_time) * 1000)

            # Handle different response formats (Falcon vs Llama)
            if isinstance(response, list):
                # Falcon-style response: Retrieve generated text from the list
                generated_text = response[0].get('generated_text', '') if response else ''
            elif isinstance(response, dict):
                # Llama-style response: Retrieve generated text from the dictionary
                generated_text = response.get('generated_text', '')
            else:
                raise ValueError(f"Unexpected response format: {type(response)}")
            
            # Process the generated text to extract the answer
            if "The final answer is:" in generated_text:
                answer = generated_text.split("The final answer is:")[1].strip()
            elif "Assistant:" in generated_text:
                answer = generated_text.split("Assistant:")[1].strip()
            else:
                answer = generated_text.strip()

            # Clean and validate the response
            cleaned_response = self._clean_response(answer)
            
            # Final validation of the generated text
            if not cleaned_response or cleaned_response.isspace() or 'DRAFT' in cleaned_response:
                return "Unable to generate a proper response. Please try again."

            # SageMaker does not provide input tokens as metadata.
            # As a workaround, we use a rough approximation: ~4 characters per token.
            input_tokens = len(prompt) // 4
            output_tokens = len(generated_text) // 4
            total_tokens = input_tokens + output_tokens
            
            answer_metadata = {
                'inputTokens': input_tokens,
                'outputTokens': output_tokens,
                'totalTokens': total_tokens,
                'latencyMs': latency
            }
            
            return answer_metadata, cleaned_response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Error generating response: {str(e)}"

    def _clean_response(self, text: str) -> str:
        """
        Cleans and formats the response text by removing common artifacts, ensuring proper sentence structure,
        and eliminating excessive whitespace or newlines.

        Args:
            text (str): The raw response text that needs to be cleaned.

        Returns:
            str: The cleaned and formatted response text.
        """
        # Define a list of common artifacts that should be removed
        artifacts = ['DRAFT', '[INST]', '[/INST]', 'Human:', 'Assistant:']
        
        # Remove any leading/trailing whitespace and clean artifacts from the text
        cleaned_text = text.strip()
        for artifact in artifacts:
            cleaned_text = cleaned_text.replace(artifact, '').strip()

        # Ensure the response ends with a proper sentence-ending punctuation mark (., !, or ?)
        sentence_endings = ['.', '!', '?']
        
        # Check if the text ends with one of the valid sentence-ending punctuation marks
        if not any(cleaned_text.rstrip().endswith(end) for end in sentence_endings):
            # Find the position of the last sentence-ending punctuation mark in the text
            last_period = max(
                cleaned_text.rfind('.'),
                cleaned_text.rfind('!'),
                cleaned_text.rfind('?')
            )
            
            # If a punctuation mark is found, truncate the text to that position
            if last_period != -1:
                cleaned_text = cleaned_text[:last_period + 1]

        # Remove multiple consecutive spaces and newlines, replace them with a single space
        cleaned_text = ' '.join(cleaned_text.split())
        
        think_end_index = cleaned_text.find('</think>')
        if think_end_index != -1:
            cleaned_text = cleaned_text[think_end_index + len('</think>'):]

        # Return the cleaned text, ensuring no extra spaces around it
        return cleaned_text.strip()
    
    def _initialize_client(self) -> None:
        raise NotImplementedError("Subclasses must implement `_initialize_client`")
    
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