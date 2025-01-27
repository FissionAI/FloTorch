from typing import Any, Dict, Optional, List, Union
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
    chunk_size: Union[int, List] = Field(alias="chunk_size")
    chunk_overlap: Union[int, List] = Field(alias="chunk_overlap")
    hierarchical_parent_chunk_size: int = Field(alias="hierarchical_parent_chunk_size")
    hierarchical_child_chunk_size: int = Field(alias="hierarchical_child_chunk_size")
    hierarchical_chunk_overlap_percentage: int = Field(alias="hierarchical_chunk_overlap_percentage")
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
    vector_dimension: Union[int, List] = Field(alias="vector_dimension")
    enable_guardrails: bool = False
    guardrail_id: Optional[str] = None
    guardrail_version: Optional[str] = None
    enable_prompt_guardrails: bool = False
    enable_context_guardrails: bool = False
    enable_response_guardrails: bool = False
    # This should ideally work need furthur debugging
    llm_based_eval: bool = True
    eval_service: str = 'ragas'
    eval_embedding_model: str = 'amazon.titan-embed-text-v1'
    eval_retrieval_model: str = 'mistral.mixtral-8x7b-instruct-v0:1'
    eval_retrieval_temperature: float = float(0.4)
    # Rerank model id
    rerank_model_id: str = Field(alias="rerank_model_id", default="none")
    bedrock_knowledge_base: bool = False
    class Config:
        alias_generator = lambda string: string.replace("-", "_")
        populate_by_name = True

class NShotPromptGuide(BaseModel):
    system_prompt: str
    examples: Optional[list[dict[str, str]]] = Field(default=None)
    user_prompt: str
