import logging
from typing import List, Dict

from baseclasses.base_classes import BaseEvaluator
from core.dynamodb import DynamoDBOperations

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RagasEvaluator(BaseEvaluator):

    def __init__(self, config, experimental_config):
        super().__init__(config, experimental_config)
        self._initialize_dynamodb()

    def _initialize_dynamodb(self):
        """Initialize DynamoDB connections"""
        self.metrics_db = DynamoDBOperations(
            region=self.config.aws_region,
            table_name=self.config.experiment_question_metrics_table
        )
        self.experiment_db = DynamoDBOperations(
            region=self.config.aws_region,
            table_name=self.config.experiment_table
        )

    def get_all_questions(self, experiment_id: str) -> List[Dict]:
        """Fetch all questions for a given experiment"""
        expression_values = {":experimentId": experiment_id}
        return self.metrics_db.query(
            "experiment_id = :experimentId",
            expression_values=expression_values,
            index_name=self.config.experiment_question_metrics_experimentid_index
        )

    def update_experiment_metrics(self, experiment_id: str, experiment_eval_metrics: Dict[str, float]):
        """Update overall experiment metrics"""
        try:
            if experiment_eval_metrics:
                logger.info(f"Updating experiment metrics for experiment {experiment_id}")
                self.experiment_db.update_item(
                    key={'id': experiment_id},
                    update_expression="SET eval_metrics = :eval",
                    expression_values={':eval': {'M': experiment_eval_metrics}}
                )
        except Exception as e:
            logger.error(f"Error updating experiment metrics: {e}")

    def calculate_eval_score(self, evaluator, data):
        try:
            score = evaluator.single_turn_score(data)
            return score
        except Exception as e:
            logger.error(f"Error processing sample : {e}")
            return 0.0
