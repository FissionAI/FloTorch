from core.eval.ragas.ragas_llm_eval import RagasLLMEvaluator
from langchain_aws import ChatBedrockConverse, BedrockEmbeddings
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from core.eval.eval_factory import EvalFactory

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class RagasLLMBedrockEvaluator(RagasLLMEvaluator):
    def __init__(self, config, experimental_config):
        super().__init__(config, experimental_config)


    def _initialze_llm(self):
        try:
            self.evaluator_llm = LangchainLLMWrapper(ChatBedrockConverse(
                    region_name=self.experimental_config.aws_region,
                    base_url=f"https://bedrock-runtime.{self.experimental_config.aws_region}.amazonaws.com",
                    model=self.experimental_config.eval_retrieval_model,
                    temperature=self.experimental_config.eval_retrieval_temperature,
                    ))

            self.embedding_llm = LangchainEmbeddingsWrapper(BedrockEmbeddings(
                region_name=self.experimental_config.aws_region,
                model_id=self.experimental_config.eval_embedding_model,
            ))
        except Exception as e:
            logging.error(f"Failed to initialize LLM: {e}")

EvalFactory.register_evaluator('ragas', 'bedrock',  RagasLLMBedrockEvaluator)