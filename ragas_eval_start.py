import os
import json
from typing import List, Dict
import requests
import pandas as pd
from loguru import logger
from tqdm.auto import tqdm

# Constants
DEFAULT_BATCH_SIZE = 8
MAX_TOKENS = 100


# from lambda_handlers.indexing_handler import lambda_handler as indexing
# from lambda_handlers.retriever_handler import lambda_handler as retriever

# from core.service.experimental_config_service import ExperimentalConfigService
# from config.config import Config
# from retriever.retriever import retrieve

# import ragas script file for existing methods
from core.eval.ragas.ragas_llm_eval import RagasLLMEvaluator # RagasLLMEvaluator


# def readDataObjects(data, size):
#     return {"file location": data, "size": size}


# def load_bulk_data(data, size):
#     matrix = pd.read_csv(data)
#     file_path = readDataObjects(data, size)
#     json_data = {
#         "id": matrix['id'],
#         "question": matrix['question'],
#         "file location": file_path
#     }
#     return dict(json_data)


def load_data_in_batches(dataset_path: str, batch_size: int = DEFAULT_BATCH_SIZE):
    """Yield batches of data from a CSV file."""
    if not os.path.exists(dataset_path):
        logger.error(f"File not found: {dataset_path}")
        raise FileNotFoundError(f"The file {dataset_path} was not found.")

    def initialize_batch():
        return {"id": [], "question": [], "answer_metadata": [], "execution_id": [], "experiment_id": [], "generated_answer": [], "gt_answer": [], "query_metadata": [], "reference_contexts": [], "timestamp": []}

    for chunk in pd.read_csv(dataset_path, chunksize=batch_size):
        batch = initialize_batch()
        # print(batch.items())
        for col in batch.keys():
            batch[col].extend(chunk[col])
        yield batch


def send_batch_request(batch: Dict[str, List[str]], chunksize: str):
    """Send batch queries to the Ragas class."""
    responses = []

    for anwers in batch["generated_answer"]:
        # print(query)
        responses.append(anwers)

    return responses


def ragas_evaluation(dataset_path, batch_size):

    matrix = []

    for batch in tqdm(load_data_in_batches(dataset_path, batch_size), desc="Generating predictions"):
        # Extract relevant fields from the batch
        interaction_ids = batch.pop("id", [])
        answer_metadata = batch.pop("answer_metadata", [])
        execution_id = batch.pop("execution_id", [])
        experiment_id = batch.pop("experiment_id", [])
        generated_answer = batch.get("generated_answer", [])
        gt_answer = batch.pop("gt_answer", [])
        query_metadata = batch.pop("query_metadata", [])
        reference_contexts = batch.pop("reference_contexts", [])
        timestamp = batch.pop("timestamp")
        queries = batch.get("question", [])

        # Send the batch for API processing
        responses = send_batch_request(batch, batch_size)
        print("\n================Response=================== \n",responses, batch_size)

        # Process each query in the batch
        for idx, response in enumerate(responses):
            result = {
                "id": interaction_ids[idx] if idx < len(interaction_ids) else None,
                "answer_metadata": answer_metadata[idx] if idx < len(answer_metadata) else None,
                "execution_id": execution_id[idx] if idx < len(execution_id) else None,
                "experiment_id": experiment_id[idx] if idx < len(experiment_id) else None,
                # "generated_answer": generated_answer[idx] if idx < len(generated_answer) else None,
                "gt_answer": gt_answer[idx] if idx < len(gt_answer) else None,
                "query_metadata": query_metadata[idx] if idx < len(query_metadata) else None,
                # "reference_contexts": reference_contexts[idx] if idx < len(reference_contexts) else None,
                "timestamp": timestamp[idx] if idx < len(timestamp) else None,
                "query": queries[idx] if idx < len(queries) else None,
                "response": response,
            }
            matrix.append(result)
    
    return matrix


def save_to_json(data: List[Dict], output_path: str):
    """Save structured data to a JSON file."""
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)
    logger.info(f"Data saved to {output_path}")


if __name__ == "__main__":
    DATASET_PATH = "/Users/FL_LPT-359/Documents/RagasData/AWSdynamoDB_dataset/AmazonBedrock_946RI6BP.csv"
    print(DATASET_PATH)
    if DATASET_PATH:
        BATCH_SIZE = 8
        results = ragas_evaluation(DATASET_PATH, BATCH_SIZE)
        print("printed results")
        import time
        created = time.time()
        save_to_json(results, output_path="wsr/"+str(created)+"_results.json")
    else:
        print(f"Please select correct file name and this {DATASET_PATH} is not correct!")