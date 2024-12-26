from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from typing import Optional
from pydantic import Field
import uuid
import time
import logging
from dataclasses import dataclass
from config.config import Config
from config.experimental_config import ExperimentalConfig, NShotPromptGuide
from core.dynamodb import DynamoDBOperations
import random
from dataclasses import dataclass, asdict
from decimal import Decimal
import botocore


logger = logging.getLogger(__name__)
#Vector Datastore
class VectorDatabase(ABC):
    @abstractmethod
    def create_index(self, index_name: str, mapping: Dict[str, Any], algorithm: str) -> None:
        """Create a new index with the specified mapping and algorithm."""
        pass

    @abstractmethod
    def update_index(self, index_name: str, new_mapping: Dict[str, Any]) -> None:
        """Update an existing index with a new mapping."""
        pass

    @abstractmethod
    def delete_index(self, index_name: str) -> None:
        """Delete an existing index."""
        pass

    @abstractmethod
    def insert_document(self, index_name: str, document: Dict[str, Any]) -> None:
        """Insert a document into the specified index."""
        pass

    @abstractmethod
    def search(self, index_name: str, query_vector: List[float], k: int) -> List[Dict[str, Any]]:
        """Perform a vector search on the specified index."""
        pass

class BaseInferencer(ABC):
    
    def __init__(self, model_id: str, experiment_config : ExperimentalConfig,region: str = 'us-east-1'):
        self.model_id = model_id
        self.region = region
        self.experiment_config = experiment_config
        self._initialize_client()

    @abstractmethod
    def _initialize_client(self) -> None:
        """Initialize the appropriate client"""
        pass

    @abstractmethod
    def generate_text(self, user_query: str, context: List[Dict], default_prompt: str, **kwargs) -> str:
        """Generate text based on input"""
        pass

    def get_model_id(self) -> str:
        """Return the model ID."""
        return self.model_id


class ExperimentQuestionMetrics(BaseModel):
    id : str = Field(default_factory=lambda: str(uuid.uuid4()), description="The unique identifier for the question")
    execution_id : str = Field(..., description="The execution id")
    experiment_id: str = Field(..., description="The unique identifier for the experiment")
    timestamp: datetime = Field(default_factory=datetime.now, description="The timestamp of the experiment")
    question: str = Field(..., description="The question that was asked")
    gt_answer: str = Field(..., description="The answer that was given")
    generated_answer: str = Field(default='', description="The answer that was generated")
    reference_contexts:  Optional[List[str]] = Field(..., description="The reference contexts retrieved from vectorstore") 
    query_metadata: Optional[Dict[str, int]] = Field(..., description="The metadata during querying")
    answer_metadata: Optional[Dict[str, int]] = Field(..., description="The metadata during answer generation")

    def to_dynamo_item(self) -> Dict[str, Dict[str, str]]:
        """Convert to DynamoDB item format."""
        return {
            'id' : {'S': self.id},
            'execution_id': {'S': self.execution_id},
            'experiment_id': {'S': self.experiment_id},
            'question': {'S': self.question},
            'gt_answer': {'S': self.gt_answer},
            'generated_answer': {'S': self.generated_answer},
            'reference_contexts': {
                'L': [{'S': context} for context in self.reference_contexts]
            },
            'query_metadata': {
                'M': {key: {'N': str(value)} for key, value in self.query_metadata.items()}
            },
            'answer_metadata': {
                'M': {key: {'N': str(value)} for key, value in self.answer_metadata.items()}
            }
        } 



class BaseChunker(ABC):
    """Abstract base class for chunking strategies."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        """Abstract method for chunking text."""
        pass


class BaseEmbedder(ABC):
    """Abstract base class for all embedders."""

    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    @abstractmethod
    def prepare_payload(self, text: str, dimensions: int, normalize: bool) -> Dict:
        pass

    @abstractmethod
    def embed(self, text: str, dimensions: int = 256, normalize: bool = True) -> List[float]:
        pass

    def get_model_id(self) -> str:
        return self.model_id
    
class BaseEvaluator(ABC):

    def __init__(self, config: Config, experimental_config: ExperimentalConfig) -> None:
        self.config = config
        self.experimental_config = experimental_config
        self._initialize_dynamodb()

    @abstractmethod
    def _initialize_scorers(self) -> None:
        """Initialize the appropriate scorers"""
        pass

    @abstractmethod
    def evaluate(self, question: str, generated_answer: str, gt_answer: str, reference_contexts: List[str]) -> 'EvaluationMetrics':
        """Evaluate the generated answer against the ground truth answer."""
        pass 

    @abstractmethod
    def get_questions(self, experiment_id: str) -> List[Dict]:
        pass

    @abstractmethod
    def update_experiment_metrics(self, experiment_id: str, metrics_list: List['EvaluationMetrics']):
        pass

# Experiment
class Experiment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    execution_id: str
    start_datetime: datetime = Field(default_factory=datetime.now)
    end_datetime: Optional[datetime] = None
    config: Dict[str, Any]
    experiment_status: str = "not_started"
    index_status: str = "not_started"
    retrieval_status: str = "not_started"
    index_id: Optional[str] = None
    indexing_time: int = 0
    retrieval_time: int = 0
    total_time: int = 0
    cost: float = 0.0
    eval_metrics: Dict[str, Any] = Field(default_factory=dict)


# Execution
class Execution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: datetime = Field(default_factory=datetime.now)
    config: Dict[str, Any]
    status: str = "not_started"
    gt_data: str
    kb_data: str
    region: str
    name: str

@dataclass
class EvaluationMetrics():
    faithfulness_score: Optional[float] = 0.0
    context_precision_score: Optional[float] = 0.0
    aspect_critic_score: Optional[float] = 0.0
    answers_relevancy_score: Optional[float] = 0.0
    string_similarity: Optional[float] = 0.0
    context_recall: Optional[float] = 0.0
    rouge_score: Optional[float] = 0.0


    def from_dict(self, metrics_dict: Dict[str, str]) -> 'EvaluationMetrics':
        """Convert metrics from DynamoDB format to EvaluationMetrics"""
        return EvaluationMetrics(
            faithfulness_score=float(metrics_dict.get('faithfulness', '0.0')),
            context_precision_score=float(metrics_dict.get('llm_context_precision_without_reference', '0.0')),
            aspect_critic_score=float(metrics_dict.get('maliciousness', '0.0')),
            answers_relevancy_score=float(metrics_dict.get('answer_relevancy', '0.0')),
            string_similarity=float(metrics_dict.get('String_Similarity', '0.0')),
            context_recall=float(metrics_dict.get('Context_Recall', '0.0')),
            rouge_score=float(metrics_dict.get('Rouge_Score', '0.0'))
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            'faithfulness_score': str(self.faithfulness_score),
            'context_precision_score': str(self.context_precision_score),
            'aspect_critic_score': str(self.aspect_critic_score),
            'answers_relevancy_score': str(self.answers_relevancy_score),
            'string_similarity_score': str(self.string_similarity),
            'context_recall_score': str(self.context_recall),
            'rouge_score': str(self.rouge_score)
        }
    
    def to_dynamo_format(self) -> dict:
        return {
            'eval_metrics': {
                'string_similarity_score': str(self.string_similarity) if self.string_similarity is not None else '0.0',
                'context_recall_score': str(self.context_recall) if self.context_recall is not None else '0.0',
                'rouge_score': str(self.rouge_score) if self.rouge_score is not None else '0.0',
                'faithfulness_score': str(self.faithfulness_score) if self.faithfulness_score is not None else '0.0',
                'context_precision_score': str(self.context_precision_score) if self.context_precision_score is not None else '0.0',
                'aspect_critic_score': str(self.aspect_critic_score) if self.aspect_critic_score is not None else '0.0',
                'answers_relevancy_score': str(self.answers_relevancy_score) if self.answers_relevancy_score is not None else '0.0'
            }
        }
    
    def to_dynamo_format(self) -> Dict[str, Dict[str, str]]:
        """Convert metrics to DynamoDB format"""
        return {
            'Faithfulness': {'S': str(self.faithfulness_score) if self.faithfulness_score is not None else '0.0'},
            'Context_Precision': {'S': str(self.context_precision_score) if self.context_precision_score is not None else '0.0'},
            'Aspect_Critic': {'S': str(self.aspect_critic_score) if self.aspect_critic_score is not None else '0.0'},
            'Answers_Relevancy': {'S': str(self.answers_relevancy_score) if self.answers_relevancy_score is not None else '0.0'},
            'String_Similarity': {'S': str(self.string_similarity) if self.string_similarity is not None else '0.0'},
            'Context_Precision': {'S': str(self.context_precision) if self.context_precision is not None else '0.0'},
            'Context_Recall': {'S': str(self.context_recall) if self.context_recall is not None else '0.0'},
            'Rouge_Score': {'S': str(self.rouge_score) if self.rouge_score is not None else '0.0'}
        }


class RetryParams(BaseModel):
    max_retries: int
    retry_delay: int
    backoff_factor: int
    
class BotoRetryHandler(ABC):
    """Abstract class for retry handler"""
    
    @property
    @abstractmethod
    def retry_params(self) -> RetryParams:
        pass
    
    @property
    @abstractmethod
    def retryable_errors(self) -> set[str]:
        pass
        
        
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            retries = 0
            retry_params = self.retry_params
            while retries < retry_params.max_retries:
                try:
                    return func(*args, **kwargs)
                except botocore.exceptions.ClientError as e:
                    error_code = e.response['Error']['Code']
                    if error_code in self.retryable_errors:
                        retries += 1
                        logger.error(f"Rate limit error in Bedrock converse (Attempt {retries}/{retry_params.max_retries}): {str(e)}")
                        
                        if retries >= retry_params.max_retries:
                            logger.error("Max retries reached. Could not complete Bedrock converse operation.")
                            raise
                        
                        backoff_time = retry_params.retry_delay * (retry_params.backoff_factor ** (retries - 1))
                        logger.info(f"Retrying in {backoff_time} seconds...")
                        time.sleep(backoff_time)
                    else:
                        # If it's not a rate limit error, raise immediately
                        raise
                except Exception as e:
                    # For any other exception, log and raise immediately
                    logger.error(f"Unexpected error in Bedrock converse: {str(e)}")
                    raise
            
        return wrapper