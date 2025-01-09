from core.dynamodb import DynamoDBOperations
from typing import Dict, Any, Optional
from config.experimental_config import ExperimentalConfig, NShotPromptGuide
from util.dynamo_utils import deserialize_dynamodb_json
from config.config import Config

class ExperimentalConfigService:
    """Service class to manage experimental configurations."""
    
    def __init__(self, config: Config):
        self.aws_region = config.aws_region
        self.experiment_db = DynamoDBOperations(
            region=self.aws_region,
            table_name=config.experiment_table
        )

    def _validate_n_shot_prompts(self, experiment_id: str, n_shot_prompt_guide: NShotPromptGuide, 
                               required_examples: int) -> None:
        """Validate n-shot prompt guide configuration."""
        if not n_shot_prompt_guide.system_prompt:
            raise ValueError(f"Experiment {experiment_id}: Missing system prompt")
        if not n_shot_prompt_guide.user_prompt:
                raise ValueError(f"Experiment {experiment_id}: Missing user prompt")
        if required_examples > 0 and len(n_shot_prompt_guide.examples) < required_examples:
            raise ValueError(
                f"Experiment {experiment_id}: Insufficient n-shot examples. "
                f"Required: {required_examples}, Found: {len(n_shot_prompt_guide.examples)}"
            )

    def create_experimental_config(self, exp_config_data: Dict[str, Any]) -> ExperimentalConfig:
        """Create and validate an experimental configuration.
        
        Args:
            exp_config_data: Dictionary containing experimental configuration parameters
            
        Returns:
            ExperimentalConfig: Validated experimental configuration object
            
        Raises:
            ValueError: If experiment doesn't exist or has invalid configuration
        """
        # Validate required fields
        experiment_id = exp_config_data.get('experiment_id')
        if not experiment_id:
            raise ValueError("experiment_id is required")

        experiment = self.experiment_db.get_item({'id': experiment_id})
        if not experiment:
            raise ValueError(f"Experiment with id {experiment_id} not found")
        
        exp_config = ExperimentalConfig(
            execution_id=exp_config_data.get('execution_id'),
            experiment_id=experiment_id,
            embedding_model=exp_config_data.get('embedding_model'),
            retrieval_model=exp_config_data.get('retrieval_model'),
            vector_dimension=exp_config_data.get('vector_dimension', 0),
            gt_data=exp_config_data.get('gt_data', {}),
            index_id=exp_config_data.get('index_id'),
            knn_num=exp_config_data.get('knn_num', 1),
            temp_retrieval_llm=exp_config_data.get('temp_retrieval_llm'),
            embedding_service=exp_config_data.get('embedding_service'),
            retrieval_service=exp_config_data.get('retrieval_service'),
            aws_region=exp_config_data.get('aws_region', self.aws_region),
            chunking_strategy=exp_config_data.get('chunking_strategy'),
            chunk_size=exp_config_data.get('chunk_size', 0),
            chunk_overlap=exp_config_data.get('chunk_overlap', 0),
            hierarchical_parent_chunk_size=exp_config_data.get('hierarchical_parent_chunk_size', 0),
            hierarchical_child_chunk_size=exp_config_data.get('hierarchical_child_chunk_size', 0),
            hierarchical_chunk_overlap_percentage=exp_config_data.get('hierarchical_chunk_overlap_percentage', 0),
            kb_data=exp_config_data.get('kb_data', {}),
            n_shot_prompts=exp_config_data.get('n_shot_prompts', 0),
            indexing_algorithm=exp_config_data.get('indexing_algorithm'),
            rerank_model_id=exp_config_data.get('rerank_model_id', "none"),
            enable_guardrails=exp_config_data.get("enable_guardrails", False),
            guardrail_id=exp_config_data.get("guardrail_id", ""),
            guardrail_version=exp_config_data.get("guardrail_version", ""),
            enable_prompt_guardrails=exp_config_data.get("enable_prompt_guardrails", False),
            enable_context_guardrails=exp_config_data.get("enable_context_guardrails", False),
            enable_response_guardrails=exp_config_data.get("enable_response_guardrails", False),
            eval_service=exp_config_data.get('eval_service', "ragas"),
            eval_embedding_model=exp_config_data.get('eval_embedding_model', "amazon.titan-embed-text-v1"),
            eval_retrieval_model=exp_config_data.get('eval_retrieval_model', "mistral.mixtral-8x7b-instruct-v0:1"),
        )

        n_shot_prompt_guide = experiment.get('config').get('n_shot_prompt_guide')
        if not n_shot_prompt_guide:
            raise ValueError(f"Experiment {experiment_id}: Missing prompt file")

        n_shot_prompt_guide = NShotPromptGuide(**deserialize_dynamodb_json(n_shot_prompt_guide))
        self._validate_n_shot_prompts(experiment_id, n_shot_prompt_guide, exp_config.n_shot_prompts)
        
        exp_config.n_shot_prompt_guide_obj = n_shot_prompt_guide

        return exp_config
