import logging

from config.experimental_config import ExperimentalConfig
from core.processors import EvalProcessor

logger = logging.getLogger(__name__)


def evaluate(experiment_config: ExperimentalConfig):
    try:
        EvalProcessor(experiment_config).evaluate()
    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        raise
