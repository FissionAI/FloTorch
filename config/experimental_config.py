from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import json 
import re

class ExperimentalConfig(BaseModel):

    execution_id: str
    experiment_id: str 
    aws_region: str = Field(alias="aws_region")
    kb_data: str = Field(alias="kb_data")
    gt_data: str = Field(alias="gt_data")
    chunking_strategy: str = Field(alias="chunking_strategy")
    chunk_size: int = Field(alias="chunk_size")
    chunk_overlap: int = Field(alias="chunk_overlap")
    embedding_service: str = Field(alias="embedding_service")
    embedding_model: str = Field(alias="embedding_model")
    embedding_model_endpoint: str = None 
    indexing_algorithm: str = Field(alias="indexing_algorithm")
    index_id: str = Field(alias="index_id")
    n_shot_prompts: int = Field(alias="n_shot_prompts")
    n_shot_prompt_guide: Optional[str] = None
    n_shot_prompt_guide_obj: 'NShotPromptGuide' = None
    knn_num: int = Field(alias="knn_num")
    temp_retrieval_llm: float = Field(alias="temp_retrieval_llm")
    retrieval_service: str = Field(alias="retrieval_service")
    retrieval_model: str = Field(alias="retrieval_model")
    retrieval_model_endpoint: str = None
    vector_dimension: int = Field(alias="vector_dimension")
    # This should ideally work need furthur debugging
    llm_based_eval: bool = True
    eval_service: str = 'ragas'
    ragas_embedding_llm: str = 'amazon.titan-embed-text-v1'
    ragas_inference_llm: str = 'mistral.mixtral-8x7b-instruct-v0:1'
    ragas_inference_temperature: float = float(0.4)
    # Rerank model id
    rerank_model_id: str = Field(alias="rerank_model_id", default="none")
    class Config:
        alias_generator = lambda string: string.replace("-", "_")
        populate_by_name = True

class NShotPromptGuide(BaseModel):
    system_prompt: str
    examples: Optional[list[dict[str, str]]] = Field(default=None)
    user_prompt: str
