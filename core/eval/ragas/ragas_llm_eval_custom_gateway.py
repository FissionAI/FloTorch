from core.eval.ragas.ragas_llm_eval import RagasLLMEvaluator
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from core.eval.eval_factory import EvalFactory

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class RagasLLMEvaluatorCustomGateway(RagasLLMEvaluator):
    def __init__(self, config, experimental_config):
        super().__init__(config, experimental_config)

    def _initialze_llm(self):
        try:
            gateway_url = f'{getattr(self.experimental_config, "gateway_url", "")}/api/openai/v1'
            temperature = getattr(self.experimental_config, 'eval_retrieval_temperature', 0.4)
            self.evaluator_llm = LangchainLLMWrapper(ChatOpenAI(
                base_url=gateway_url,
                api_key=self.experimental_config.gateway_api_key,
                model=self.experimental_config.eval_retrieval_model,
                temperature=temperature,
            ))

            self.embedding_llm = LangchainEmbeddingsWrapper(OpenAIEmbeddings(
                model=self.experimental_config.eval_embedding_model,
                base_url=gateway_url,
                api_key=self.experimental_config.gateway_api_key,
            ))
        except Exception as e:
            logging.error(f"Failed to initialize LLM: {e}")

EvalFactory.register_evaluator('ragas', 'custom_gateway', RagasLLMEvaluatorCustomGateway)