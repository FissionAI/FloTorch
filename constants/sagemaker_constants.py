from typing import Final, Dict


class SageMakerInstanceConstants:
    INSTANCE_CONFIGS: Final[Dict[str, str]] = {
        "BAAI/bge-large-en-v1.5": "ml.g5.2xlarge",
        "Qwen/Qwen2.5-32B-Instruct": "g6e.12xlarge",
        "Qwen/Qwen2.5-14B-Instruct": "g6e.2xlarge",
        "meta-llama/Llama-3.1-8B": "ml.g5.2xlarge",
        "meta-llama/Llama-3.1-70B-Instruct": "g6e.12xlarge"
    }
