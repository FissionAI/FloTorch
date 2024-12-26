from baseclasses.base_classes import BaseInferencer
import boto3
from typing import List, Dict, Any, Union, Tuple
import logging
from config.experimental_config import ExperimentalConfig, NShotPromptGuide
from core.inference.inference_factory import InferencerFactory
from util.boto3_utils import BedRockRetryHander
import random

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Class for handling inference using Amazon Bedrock 
class BedrockInferencer(BaseInferencer):
    """Base class for all Bedrock models since they share the same invocation pattern"""

    def _initialize_client(self) -> None:
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=self.region
        )

    def generate_prompt(self, experiment_config: ExperimentalConfig, default_prompt: str, user_query: str, context: List[Dict]):
        # Get n_shot config values first to avoid repeated lookups
        n_shot_prompt_guide = experiment_config.n_shot_prompt_guide_obj
        n_shot_prompt = experiment_config.n_shot_prompts

        # Input validation
        if n_shot_prompt < 0:
            raise ValueError("n_shot_prompt must be non-negative")
        
        # Get system prompt
        system_prompt = default_prompt if n_shot_prompt_guide is None or n_shot_prompt_guide.system_prompt is None else n_shot_prompt_guide.system_prompt
        
        context_text = self._format_context(context)
        
        base_prompt = n_shot_prompt_guide.user_prompt if n_shot_prompt_guide.user_prompt else ""
        
        # Return early if no examples needed
        if n_shot_prompt == 0:
            # Use string concatenation
            logger.info("into zero shot prompt")
            prompt = (
                system_prompt + "\n\n" + 
                "<context>\n" + 
                context_text + "\n" + 
                "</context>\n" + 
                base_prompt + "\n" + 
                "Question: " + user_query
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
        # Use string concatenation for the entire prompt
        prompt = (
            system_prompt + "\n\n" + 
            "Few examples:\n" + 
            example_text + "\n" + 
            "<context>\n" + 
            context_text + "\n" + 
            "</context>\n" + 
            base_prompt + "\n" + 
            "Question: " + user_query
        )
        
        return prompt.strip()
     
    @BedRockRetryHander()
    def generate_text(self, user_query: str, context: List[Dict], default_prompt: str, **kwargs) -> Tuple[Dict[Any, Any], str]:
        try:
            # Code to generate prompt considering the upload prompt config file
            converse_prompt = self.generate_prompt(self.experiment_config, default_prompt, user_query, context)
            messages = self._prepare_payload(context, converse_prompt, user_query)
            inference_config={"maxTokens": 512, "temperature": self.experiment_config.temp_retrieval_llm, "topP": 0.9}
            response = self.client.converse(
                modelId=self.model_id,
                messages=messages,
                inferenceConfig=inference_config
            )
            metadata = {}
            if 'usage' in response:
                for key, value in response['usage'].items():
                    metadata[key] = value
            if 'metrics' in response:
                for key, value in response['metrics'].items():
                    metadata[key] = value
            return metadata, self._extract_response(response)
        except Exception as e:
            logger.error(f"Error generating text with Bedrock: {str(e)}")
            raise

    def _prepare_payload(self, context: List[Dict], prompt: str, user_query: str):
        # Format context documents into a single string
        context_text = self._format_context(context)
        logger.debug(f"Formatted context text length: {len(context_text)}")

        conversation = [
            {
                "role": "user", 
                "content": [{"text" : f"{prompt}"}]
            }
        ]
        return conversation

    def _format_context(self, context: List[Dict[str, str]]) -> str:
        """Format context documents into a single string."""
        context_text = "\n".join([
            f"Context {i+1}:\n{doc.get('text', '')}"
            for i, doc in enumerate(context)
        ])
        logger.debug(f"Formatted context text length: {len(context_text)}")
        return context_text

    def _extract_response(self, response: Dict) -> str:
        """Extract text from Bedrock response."""
        response_text = response["output"]["message"]["content"][0]["text"]
        logger.info("Successfully generated response")
        logger.debug(f"Response length: {len(response_text)}")
        return response_text
    
    
model_list = ["mistral.mistral-7b-instruct-v0:2",
              "mistral.mistral-large-2402-v1:0",
              "us.meta.llama3-2-90b-instruct-v1:0",
              "us.meta.llama3-2-11b-instruct-v1:0",
              "us.meta.llama3-2-3b-instruct-v1:0",
              "us.meta.llama3-2-1b-instruct-v1:0",
              "cohere.command-r-v1:0",
              "cohere.command-r-plus-v1:0",
              "anthropic.claude-3-5-sonnet-20240620-v1:0",
              "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
              "amazon.titan-text-express-v1",
              "amazon.titan-text-lite-v1",
              "amazon.nova-lite-v1:0",
              "amazon.nova-micro-v1:0",
              "amazon.nova-pro-v1:0"
              ]

for model in model_list:
    InferencerFactory.register_inferencer('bedrock', model, BedrockInferencer)
    
    