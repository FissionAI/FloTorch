import logging

from config.experimental_config import ExperimentalConfig
from core.eval.eval_factory import EvalFactory

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class EvalProcessor:
    """Processor for embedding text chunks."""

    def __init__(self, experimentalConfig: ExperimentalConfig) -> None:
        self.experimentalConfig = experimentalConfig
        self.evaluator = EvalFactory.create_evaluator(experimentalConfig)

    def evaluate(self) -> None:
        try:
            self.evaluator.evaluate(experiment_id=self.experimentalConfig.experiment_id)
        except Exception as e:
            logger.error(f"Error generating eval: {str(e)}")
            raise
