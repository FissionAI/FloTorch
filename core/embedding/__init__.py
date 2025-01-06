from core.embedding.embedding_factory import EmbedderFactory  # Keep this for external usage.

import core.embedding.bedrock.cohere_embedder
import core.embedding.bedrock.titanv1_embedder
import core.embedding.bedrock.titanv2_embedder

# Importing SageMaker-specific embedder and embedding factory.
from .embedding_factory import EmbedderFactory
from .sagemaker import SageMakerEmbedder

# List of model names that you want to register with the EmbedderFactory
model_list = [
                "huggingface-sentencesimilarity-bge-large-en-v1-5", # Model for sentence similarity (BGE, Large).
                "huggingface-sentencesimilarity-bge-m3", # Another sentence similarity model (BGE, M3).
                "huggingface-textembedding-gte-qwen2-7b-instruct" # Text embedding model (Qwen2-7B, Instruct).
             ]

# Registering each model from the list into the EmbedderFactory under 'sagemaker'.
# The `SageMakerEmbedder` will be used for embedding operations for these models.
for model in model_list:
    EmbedderFactory.register_embedder('sagemaker', model, SageMakerEmbedder)