from .bedrock.bedrock_inferencer import BedrockInferencer

# Importing SageMaker-specific inference and inference factory.
from .inference_factory import InferencerFactory
from .sagemaker.sagemaker_inferencer import SageMakerInferencer

# List of model names that you want to register with the InferencerFactory
model_list = [
                "meta-textgeneration-llama-3-1-8b-instruct", # Model for text generation (Llama)
                "huggingface-llm-falcon-7b-instruct-bf16", # Model for text generation (Falcon)

                "meta-textgeneration-llama-3-3-70b-instruct", #Llama model with more parameters for text generation
                "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
             ]

# Registering each model from the list into the InferencerFactory under 'sagemaker'.
# The `SageMakerInferencer` will be used for inferencing operations for these models.
for model in model_list:
    InferencerFactory.register_inferencer('sagemaker', model, SageMakerInferencer)