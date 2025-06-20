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
    def search(self, query_vector: List[float], index_name: str=None, k: int=None, kb_data: str = None) -> List[Dict[str, Any]]:
        """Perform a vector search on the specified index."""
        pass

class BaseInferencer(ABC):
    
    # Added a new parameter `role_arn` as part of the SageMaker integration. 
    # The `_initialize_client` method has been commented out for now, 
    # and will be invoked within the respective inference classes when needed.
    def __init__(self, model_id: str, experiment_config: ExperimentalConfig, region: str = 'us-east-1', role_arn: str = None):
        self.model_id = model_id
        self.region_name = region
        self.experiment_config = experiment_config
        self.role_arn = role_arn
        # self._initialize_client()

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
    reference_contexts: Optional[List[str]] = Field(..., description="The reference contexts retrieved from vectorstore") 
    guardrail_input_assessment: Optional[Union[List[Dict], Dict]] = Field(default=None, description="Input guardrail assessment results")
    guardrail_context_assessment: Optional[Union[List[Dict], Dict]] = Field(default=None, description="Context guardrail assessment results")
    guardrail_output_assessment: Optional[Union[List[Dict], Dict]] = Field(default=None, description="Output guardrail assessment results")
    guardrail_id: Optional[str] = Field(default=None, description="The guardrail id that was used")
    guardrail_blocked: Optional[str] = Field(default=None, description="Input or Output blocked by Guardrail")
    eval_metrics: Optional[Dict[str, Any]] = Field(default_factory=dict)


    @staticmethod
    def _format_guardrail_assessment(assessment: Union[List[Dict], Dict]) -> Dict:
        """Format guardrail assessment for DynamoDB"""
        if not assessment:
            return None

        # Convert single dictionary to list if necessary
        if isinstance(assessment, dict):
            assessment = [assessment]

        formatted_assessment = []
        for item in assessment:
            formatted_item = {}

            # Format Topic Policy
            if 'topicPolicy' in item:
                formatted_item['topicPolicy'] = {
                    'M': {
                        'topics': {
                            'L': [
                                {
                                    'M': {
                                        'name': {'S': topic.get('name', '')},
                                        'type': {'S': topic.get('type', '')},
                                        'action': {'S': topic.get('action', '')}
                                    }
                                }
                                for topic in item['topicPolicy'].get('topics', [])
                            ]
                        }
                    }
                }

            # Format Content Policy
            if 'contentPolicy' in item:
                formatted_item['contentPolicy'] = {
                    'M': {
                        'filters': {
                            'L': [
                                {
                                    'M': {
                                        'type': {'S': filter.get('type', '')},
                                        'confidence': {'S': filter.get('confidence', '')},
                                        'filterStrength': {'S': filter.get('filterStrength', '')},
                                        'action': {'S': filter.get('action', '')}
                                    }
                                }
                                for filter in item['contentPolicy'].get('filters', [])
                            ]
                        }
                    }
                }

            # Format Word Policy
            if 'wordPolicy' in item:
                word_policy = {'M': {}}

                if 'customWords' in item['wordPolicy']:
                    word_policy['M']['customWords'] = {
                        'L': [
                            {
                                'M': {
                                    'match': {'S': word.get('match', '')},
                                    'action': {'S': word.get('action', '')}
                                }
                            }
                            for word in item['wordPolicy'].get('customWords', [])
                        ]
                    }

                if 'managedWordLists' in item['wordPolicy']:
                    word_policy['M']['managedWordLists'] = {
                        'L': [
                            {
                                'M': {
                                    'match': {'S': word.get('match', '')},
                                    'type': {'S': word.get('type', '')},
                                    'action': {'S': word.get('action', '')}
                                }
                            }
                            for word in item['wordPolicy'].get('managedWordLists', [])
                        ]
                    }

                formatted_item['wordPolicy'] = word_policy

            # Format Sensitive Information Policy
            if 'sensitiveInformationPolicy' in item:
                sensitive_info_policy = {'M': {}}

                if 'piiEntities' in item['sensitiveInformationPolicy']:
                    sensitive_info_policy['M']['piiEntities'] = {
                        'L': [
                            {
                                'M': {
                                    'match': {'S': entity.get('match', '')},
                                    'type': {'S': entity.get('type', '')},
                                    'action': {'S': entity.get('action', '')}
                                }
                            }
                            for entity in item['sensitiveInformationPolicy'].get('piiEntities', [])
                        ]
                    }

                if 'regexes' in item['sensitiveInformationPolicy']:
                    sensitive_info_policy['M']['regexes'] = {
                        'L': [
                            {
                                'M': {
                                    'name': {'S': regex.get('name', '')},
                                    'match': {'S': regex.get('match', '')},
                                    'regex': {'S': regex.get('regex', '')},
                                    'action': {'S': regex.get('action', '')}
                                }
                            }
                            for regex in item['sensitiveInformationPolicy'].get('regexes', [])
                        ]
                    }

                formatted_item['sensitiveInformationPolicy'] = sensitive_info_policy

            # Format Contextual Grounding Policy
            if 'contextualGroundingPolicy' in item:
                formatted_item['contextualGroundingPolicy'] = {
                    'M': {
                        'filters': {
                            'L': [
                                {
                                    'M': {
                                        'type': {'S': filter.get('type', '')},
                                        'threshold': {'N': str(filter.get('threshold', 0))},
                                        'score': {'N': str(filter.get('score', 0))},
                                        'action': {'S': filter.get('action', '')}
                                    }
                                }
                                for filter in item['contextualGroundingPolicy'].get('filters', [])
                            ]
                        }
                    }
                }

            # Format Invocation Metrics
            if 'invocationMetrics' in item:
                metrics = item['invocationMetrics']
                formatted_item['invocationMetrics'] = {
                    'M': {
                        'guardrailProcessingLatency': {'N': str(metrics.get('guardrailProcessingLatency', 0))},
                        'usage': {
                            'M': {
                                'topicPolicyUnits': {'N': str(metrics.get('usage', {}).get('topicPolicyUnits', 0))},
                                'contentPolicyUnits': {'N': str(metrics.get('usage', {}).get('contentPolicyUnits', 0))},
                                'wordPolicyUnits': {'N': str(metrics.get('usage', {}).get('wordPolicyUnits', 0))},
                                'sensitiveInformationPolicyUnits': {'N': str(metrics.get('usage', {}).get('sensitiveInformationPolicyUnits', 0))},
                                'sensitiveInformationPolicyFreeUnits': {'N': str(metrics.get('usage', {}).get('sensitiveInformationPolicyFreeUnits', 0))},
                                'contextualGroundingPolicyUnits': {'N': str(metrics.get('usage', {}).get('contextualGroundingPolicyUnits', 0))}
                            }
                        }
                    }
                }

            formatted_assessment.append({'M': formatted_item})

        return {'L': formatted_assessment}

    def to_dynamo_item(self) -> Dict[str, Dict[str, str]]:
        """Convert to DynamoDB item format."""
        item = {
            'id' : {'S': self.id},
            'execution_id': {'S': self.execution_id},
            'experiment_id': {'S': self.experiment_id},
            'timestamp': {'S': self.timestamp.isoformat()},
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

        # Format and add guardrail assessments if they exist
        if self.guardrail_input_assessment is not None:
            item['guardrail_input_assessment'] = self._format_guardrail_assessment(self.guardrail_input_assessment)

        if self.guardrail_context_assessment is not None:
            item['guardrail_context_assessment'] = self._format_guardrail_assessment(self.guardrail_context_assessment)

        if self.guardrail_output_assessment is not None:
            item['guardrail_output_assessment'] = self._format_guardrail_assessment(self.guardrail_output_assessment)

        if self.guardrail_id is not None:
            item['guardrail_id'] = {'S': self.guardrail_id}

        if self.guardrail_blocked is not None:
            item['guardrail_blocked'] = {'S': self.guardrail_blocked}

        return item



class BaseChunker(ABC):
    """Abstract base class for chunking strategies."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        """Abstract method for chunking text."""
        pass

class BaseHierarchicalChunker(ABC):
    """Abstract base class for chunking strategies."""

    def __init__(self, parent_chunk_size: int, child_chunk_size: int, chunk_overlap: int) -> None:
        self.parent_chunk_size = parent_chunk_size
        self.child_chunk_size = child_chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def chunk(self, text: str) -> List[List[str]]:
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
    kb_data: Union[str, List[str]]
    region: str
    name: str

@dataclass
class EvaluationMetrics():
    faithfulness_score: Optional[float] = 0.0
    context_precision_score: Optional[float] = 0.0
    aspect_critic_maliciousness_score: Optional[float] = 0.0
    aspect_critic_harmfulness_score: Optional[float] = 0.0
    aspect_critic_coherence_score: Optional[float] = 0.0
    aspect_critic_correctness_score: Optional[float] = 0.0
    aspect_critic_conciseness_score: Optional[float] = 0.0
    answers_relevancy_score: Optional[float] = 0.0
    string_similarity: Optional[float] = 0.0
    context_recall_score: Optional[float] = 0.0
    noise_sensitivity_score: Optional[float] = 0.0
    rouge_score: Optional[float] = 0.0


    def from_dict(self, metrics_dict: Dict[str, str]) -> 'EvaluationMetrics':
        """Convert metrics from DynamoDB format to EvaluationMetrics"""
        return EvaluationMetrics(
            faithfulness_score=float(metrics_dict.get('faithfulness', '0.0')),
            context_precision_score=float(metrics_dict.get('llm_context_precision_with_reference', '0.0')),
            aspect_critic_maliciousness_score=float(metrics_dict.get('maliciousness', '0.0')),
            aspect_critic_harmfulness_score=float(metrics_dict.get('harmfulness', '0.0')),
            aspect_critic_coherence_score=float(metrics_dict.get('coherence', '0.0')),
            aspect_critic_correctness_score=float(metrics_dict.get('correctness', '0.0')),
            aspect_critic_conciseness_score=float(metrics_dict.get('conciseness', '0.0')),
            answers_relevancy_score=float(metrics_dict.get('answer_relevancy', '0.0')),
            string_similarity=float(metrics_dict.get('String_Similarity', '0.0')),
            noise_sensitivity_score=float(metrics_dict.get('noise_sensitivity', '0.0')),
            context_recall_score=float(metrics_dict.get('context_recall', '0.0')),
            rouge_score=float(metrics_dict.get('Rouge_Score', '0.0'))
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            'faithfulness_score': str(self.faithfulness_score),
            'context_precision_score': str(self.context_precision_score),
            'aspect_critic_maliciousness_score': str(self.aspect_critic_maliciousness_score),
            'aspect_critic_harmfulness_score': str(self.aspect_critic_harmfulness_score),
            'aspect_critic_coherence_score': str(self.aspect_critic_coherence_score),
            'aspect_critic_correctness_score': str(self.aspect_critic_correctness_score),
            'aspect_critic_conciseness_score': str(self.aspect_critic_conciseness_score),
            'answers_relevancy_score': str(self.answers_relevancy_score),
            'string_similarity_score': str(self.string_similarity),
            'context_recall_score': str(self.context_recall_score),
            'noise_sensitivity_score': str(self.noise_sensitivity_score),
            'rouge_score': str(self.rouge_score)
        }
    
    def to_dynamo_format(self) -> dict:
        return {
            'eval_metrics': {
                'string_similarity_score': str(self.string_similarity) if self.string_similarity is not None else '0.0',
                'context_recall_score': str(self.context_recall_score) if self.context_recall_score is not None else '0.0',
                'aspect_critic_maliciousness_score': str(self.aspect_critic_maliciousness_score) if self.aspect_critic_maliciousness_score is not None else '0.0',
                'rouge_score': str(self.rouge_score) if self.rouge_score is not None else '0.0',
                'faithfulness_score': str(self.faithfulness_score) if self.faithfulness_score is not None else '0.0',
                'context_precision_score': str(self.context_precision_score) if self.context_precision_score is not None else '0.0',
                'aspect_critic_harmfulness_score': str(self.aspect_critic_harmfulness_score) if self.aspect_critic_harmfulness_score is not None else '0.0',
                'aspect_critic_coherence_score': str(self.aspect_critic_coherence_score) if self.aspect_critic_coherence_score is not None else '0.0',
                'aspect_critic_correctness_score': str(self.aspect_critic_correctness_score) if self.aspect_critic_correctness_score is not None else '0.0',
                'aspect_critic_conciseness_score': str(self.aspect_critic_conciseness_score) if self.aspect_critic_conciseness_score is not None else '0.0',
                'answers_relevancy_score': str(self.answers_relevancy_score) if self.answers_relevancy_score is not None else '0.0',
                'noise_sensitivity_score': str(self.noise_sensitivity_score) if self.noise_sensitivity_score is not None else '0.0'
            }
        }
    
    def to_dynamo_format(self) -> Dict[str, Dict[str, str]]:
        """Convert metrics to DynamoDB format"""
        return {
            'Faithfulness': {'S': str(self.faithfulness_score) if self.faithfulness_score is not None else '0.0'},
            'Context_Precision': {'S': str(self.context_precision_score) if self.context_precision_score is not None else '0.0'},
            'Aspect_Critic_Maliciousness': {'S': str(self.aspect_critic_maliciousness_score) if self.aspect_critic_maliciousness_score is not None else '0.0'},
            'Answers_Relevancy': {'S': str(self.answers_relevancy_score) if self.answers_relevancy_score is not None else '0.0'},
            'String_Similarity': {'S': str(self.string_similarity) if self.string_similarity is not None else '0.0'},
            'Noise_Sensitivity': {'S': str(self.noise_sensitivity_score) if self.noise_sensitivity_score is not None else '0.0'},
            'Aspect_Critic_Harmfulness': {'S': str(self.aspect_critic_harmfulness_score) if self.aspect_critic_harmfulness_score is not None else '0.0'},
            'Aspect_Critic_Coherence': {'S': str(self.aspect_critic_coherence_score) if self.aspect_critic_coherence_score is not None else '0.0'},
            'Aspect_Critic_Correctness': {'S': str(self.aspect_critic_correctness_score) if self.aspect_critic_correctness_score is not None else '0.0'},
            'Aspect_Critic_Conciseness': {'S': str(self.aspect_critic_conciseness_score) if self.aspect_critic_conciseness_score is not None else '0.0'},
            'Context_Recall': {'S': str(self.context_recall_score) if self.context_recall_score is not None else '0.0'},
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