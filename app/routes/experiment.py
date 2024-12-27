from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import random
import string
import traceback

from baseclasses.base_classes import Experiment
from core.dynamodb import DynamoDBOperations
from .cost_and_duration_calculation import calculate_duration, calculate_cost
from ..dependencies.database import (
    get_experiment_db, get_question_metrics_db, get_execution_db
)
from util.error_handling import create_error_response
from constants import ErrorTypes, StatusCodes
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Execution")
router = APIRouter(tags=["experiment"])

@router.post("/execution/{execution_id}/experiment")
async def post_experiment(
        execution_id: str,
        experiments: List[dict],
        status: Optional[str] = None,
        experiment_db: DynamoDBOperations=Depends(get_experiment_db),
        execution_db: DynamoDBOperations=Depends(get_execution_db)
):
    """
    Add experiments to an execution, with an optional status filter.

    Args:
        execution_id (str): The execution ID.
        experiments (List[dict]): The experiment configurations.
        status (Optional[str]): The status to filter experiments.

    Returns:
        dict: Status and the experiment IDs.
    """
    try:

        # Fetch execution details
        execution = execution_db.get_item({"id": execution_id})

        if not execution:
            raise HTTPException(
                status_code=StatusCodes.BAD_REQUEST,
                detail=create_error_response(
                    ErrorTypes.VALIDATION_ERROR,
                    "No project found for the provided ID",
                ),
            )

        if execution.get('status') != "not_started":
            raise HTTPException(
                status_code=StatusCodes.BAD_REQUEST,
                detail=create_error_response(
                    ErrorTypes.VALIDATION_ERROR,
                    "Cannot add the experiment once the execution is started",
                ),
            )

        filter_expression = "#execution_id = :execution_id"
        expression_values = {":execution_id": execution_id}
        expression_attribute_names = {"#execution_id": "execution_id"}

        existing_experiments = experiment_db.scan_all(
            filter_expression=filter_expression,
            expression_values=expression_values,
            expression_attribute_names=expression_attribute_names,
        )
        # Delete any existing experiments associated with this execution
        for experiment in existing_experiments.get("Items", []):
            experiment_db.delete_item({"id": experiment["id"]})
            
        experiment_ids = []
        for data in experiments:
            # Abbreviate the chunking strategy
            chunking_strategy = "fix" if data["chunking_strategy"].lower() == "fixed" else "hi"
            # Abbreviate the embedding service
            embedding_service = "b" if data["embedding_service"].lower() == "bedrock" else "s"
            embedding_model_mapping = {
                "amazon.titan-embed-text-v1": "amazontitanv1",
                "amazon.titan-embed-text-v2:0": "amazontitanv2",
                "amazon.titan-embed-image-v1": "amazontitanimagev1",
                "cohere.embed-english-v3": "cohereenglishv3",
                "cohere.embed-multilingual-v3": "coheremultilingualv3",
                "BAAI/bge-large-en-v1.5": "bgelargeenv1.5"  # Explicit transformation for this specific case
            }

            # Normalize the embedding model name
            embedding_model = embedding_model_mapping.get(data["embedding_model"], data["embedding_model"])

            # Generate the `index_id` with abbreviations
            index_id = (
                f"{execution_id}_{chunking_strategy}_{data['chunk_size']}_"
                f"{data['chunk_overlap']}_{embedding_service}_{embedding_model}_"
                f"{data['vector_dimension']}_{data['indexing_algorithm']}"
            ).lower()

            # Generate unique experiment ID
            experiment_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

            data['kb_data'] = execution['kb_data']
            data['gt_data'] = execution['gt_data']
            data['n_shot_prompt_guide'] = execution['config']['n_shot_prompt_guide']

            # Create the experiment record
            experiment = Experiment(
                id=experiment_id,
                execution_id=execution_id,
                config=data,
                index_id=index_id,  # Store the normalized `index_id`
                experiment_status="not_started",  # Default status
                index_status="not_started",
                retrieval_status="not_started",
                eval_status="not_started"
            )
            experiment_db.put_item(experiment.dict())
            experiment_ids.append(experiment_id)

        return {"status": "success", "experiment_ids": experiment_ids}
    except HTTPException as http_exc:
        # Re-raise the HTTPException with the same status code and detail
        raise http_exc
    except Exception as e:
        logger.error(f"Failed to create experiment: {str(e)}")
        raise HTTPException(
            status_code=StatusCodes.INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                ErrorTypes.SERVER_ERROR,
                "There is an issue while saving the experiment, please contact admin",
            ),
        )


@router.get("/execution/{execution_id}/experiment")
async def get_experiments(
        execution_id: str,
        status: Optional[str] = None,
        experiment_db=Depends(get_experiment_db)
):
    """
    Retrieve all experiments associated with a specific execution_id.
    Optionally filter by experiment_status.

    Args:
        execution_id (str): The execution ID to filter experiments.
        status (str, optional): The experiment status to filter by.

    Returns:
        List[Dict]: A list of experiments matching the criteria.
    """
    try:
        filter_expression = "#execution_id = :execution_id"
        expression_values = {":execution_id": execution_id}
        expression_attribute_names = {"#execution_id": "execution_id"}

        if status:
            filter_expression += " AND #experiment_status = :experiment_status"
            expression_values[":experiment_status"] = status
            expression_attribute_names["#experiment_status"] = "experiment_status"

        response = experiment_db.scan_all(
            filter_expression=filter_expression,
            expression_values=expression_values,
            expression_attribute_names=expression_attribute_names,
        )
        final_response = response.get("Items", [])
        final_response_with_duration = calculate_duration(final_response)
        # final_response_with_cost = calculate_cost(final_response_with_duration)
        return final_response_with_duration
    except Exception as e:
        logger.error(f"Failed to retrieve experiment: {str(e)}")
        raise HTTPException(
            status_code=StatusCodes.INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                ErrorTypes.SERVER_ERROR,
                "There is an issue while retrieving the experiment, please contact admin",
            ),
        )


@router.get("/execution/{execution_id}/experiment/{experiment_id}")
async def get_experiment(
        execution_id: str,
        experiment_id: str,
        experiment_db=Depends(get_experiment_db)
):
    experiment = experiment_db.get_item({"id": experiment_id})
    if not experiment:
        raise HTTPException(
            status_code=StatusCodes.BAD_REQUEST,
            detail=create_error_response(
                ErrorTypes.VALIDATION_ERROR,
                "No experiment found for the provided ID",
            ),
        )
    if experiment["execution_id"] != execution_id:
        raise HTTPException(
            status_code=StatusCodes.BAD_REQUEST,
            detail=create_error_response(
                ErrorTypes.VALIDATION_ERROR,
                "Experiment and Exection id mismatch",
            ),
        )
    return experiment


@router.get("/execution/{execution_id}/experiment/{experiment_id}/question_metrics")
async def get_question_metrics(
    execution_id: str,
    experiment_id: str,
    question_metrics_db=Depends(get_question_metrics_db),
):
    """
    Retrieve all question metrics for a specific execution and experiment by iterating over DynamoDB pages.

    Args:
        execution_id (str): The execution ID.
        experiment_id (str): The experiment ID.

    Returns:
        dict: All question metrics.
    """
    try:
        all_questions = []
        last_evaluated_key = None

        while True:
            # Query parameters
            
            query_params = {
                "key_condition_expression": "execution_id = :execution_id AND experiment_id = :experiment_id",
                "expression_values": {
                    ":execution_id": execution_id,
                    ":experiment_id": experiment_id,
                },
                "index_name":"execution_id-experiment_id-index",
                "projection": "generated_answer, gt_answer, question, id",
            }

            if last_evaluated_key:
                query_params["ExclusiveStartKey"] = last_evaluated_key

            # Query DynamoDB
            response = question_metrics_db.query(**query_params)

            # Append items to the result list
            all_questions.extend(response.get("Items", []))

            # Check if there are more items to fetch
            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break
        return {"question_metrics": all_questions}
    except Exception as e:
        logger.error(f"Failed to retrieve experiment: {str(e)}")
        raise HTTPException(
            status_code=StatusCodes.INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                ErrorTypes.SERVER_ERROR,
                "There is an issue while retrieving the question metrics, please contact admin",
            ),
        )
