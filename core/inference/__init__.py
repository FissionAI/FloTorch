from .bedrock.bedrock_inferencer import BedrockInferencer

# Importing SageMaker-specific inference and inference factory.
from .inference_factory import InferencerFactory
from .sagemaker.sagemaker_inferencer import SageMakerInferencer
from .sagemaker.llama_inferencer import LlamaInferencer

# List of model names that you want to register with the InferencerFactory
model_list = [
                "meta-textgeneration-llama-3-1-8b-instruct", # Model for text generation (Llama)
                "huggingface-llm-falcon-7b-instruct-bf16", # Model for text generation (Falcon)
                "meta-vlm-llama-4-scout-17b-16e-instruct",
                "meta-textgeneration-llama-3-3-70b-instruct", #Llama model with more parameters for text generation
                "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
                "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
                "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"
             ]

# Registering each model from the list into the InferencerFactory under 'sagemaker'.
# The `SageMakerInferencer` will be used for inferencing operations for these models.
for model in model_list:
    if model.startswith("meta-vlm-llama-4"):
        InferencerFactory.register_inferencer('sagemaker', model, LlamaInferencer)
    else:
        InferencerFactory.register_inferencer('sagemaker', model, SageMakerInferencer)