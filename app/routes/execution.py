from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from baseclasses.base_classes import Execution
from ..configuration_validation import generate_all_combinations
from ..dependencies.database import (
    get_execution_db,
    get_step_function_orchestrator
)
import asyncio
import random
import string
from config.config import get_config
from util.error_handling import create_error_response
from constants import ErrorTypes, StatusCodes
import logging

router = APIRouter(tags=["execution"])
config = get_config()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Execution")

@router.post("/execution")
async def post_execution(
        payload: dict,
        status: Optional[str] = None,
        execution_db=Depends(get_execution_db)
):
    """
    Create a new execution, ensuring no other execution is currently in progress.

    Args:
        payload (dict): The execution configuration payload.
        status (Optional[str]): The status to filter executions.

    Returns:
        dict: Status and the new execution ID.
    """
    try:
        # Generate unique execution ID
        execution_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))

        # Create the execution record
        execution = Execution(
            id=execution_id,
            config=payload,
            gt_data=payload["prestep"]["gt_data"],
            kb_data=payload["prestep"]["kb_data"],
            region=payload["prestep"]["region"],
            status="not_started",
            name=payload["name"]
        )

        # Save to DynamoDB
        execution_db.put_item(execution.dict())
        return {"status": "success", "execution_id": execution_id}
    except Exception as e:
        logger.error(f"Failed to create execution: {str(e)}")
        raise HTTPException(
            status_code=StatusCodes.INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                ErrorTypes.SERVER_ERROR,
                "There is an issue while saving the project, please contact admin",
            ),
        )

@router.get("/execution")
async def list_executions(
        status: Optional[str] = None,
        execution_db=Depends(get_execution_db)
):
    """
    List all executions, optionally filtered by status.
    Args:
        status (Optional[str]): Filter executions by status.

    Returns:
        List of executions.
    """
    try:
        if status:
            response = execution_db.scan(
                filter_expression="#status = :status",
                expression_values={":status": status},
                expression_attribute_names={"#status": "status"}
            )
        else:
            response = execution_db.scan()

        executions = [
            {
                "id": item.get("id", ""),
                "date": item.get("date", ""),
                "status": item.get("status", ""),
                "gt_data": item.get("gt_data", ""),
                "kb_data": item.get("kb_data", ""),
                "region": item.get("region", ""),
                "name": item.get("name", "")
            }
            for item in response.get("Items", [])
        ]
        return executions
    except Exception as e:
        logger.error(f"Failed while retrieving executions: {str(e)}")
        raise HTTPException(
            status_code=StatusCodes.INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                ErrorTypes.SERVER_ERROR,
                "An issue occurred while retrieving the projects. Please contact admin",
            ),
        )


@router.get("/execution/{id}")
async def get_execution(id: str, execution_db=Depends(get_execution_db)):
    """
    Get details of a specific execution.
    Args:
        id (str): Execution ID.

    Returns:
        Execution details.
    """
    try:
        execution = execution_db.get_item({"id": id})
        if not execution:
            raise HTTPException(
                status_code=StatusCodes.BAD_REQUEST,
                detail=create_error_response(
                    ErrorTypes.VALIDATION_ERROR,
                    "No project found for the provided ID",
                ),
            )

        result = {
            "id": execution["id"],
            "date": execution["date"],
            "status": execution["status"],
            "gt_data": execution["gt_data"],
            "kb_data": execution["kb_data"],
            "region": execution["region"],
            "config": execution["config"],
            "name": execution.get("name", ""),
        }
        return result
    except HTTPException as http_exc:
        # Re-raise the HTTPException with the same status code and detail
        raise http_exc
    except Exception as e:
        logger.error(f"Failed while retrieving execution: {str(e)}")
        raise HTTPException(
            status_code=StatusCodes.INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                ErrorTypes.SERVER_ERROR,
                "An issue occurred while retrieving the project. Please contact admin",
            ),
        )


@router.put("/execution/{id}")
async def update_execution(
        id: str,
        payload: dict,
        execution_db=Depends(get_execution_db)
):
    """
    Update an existing execution with new configuration details.

    Args:
        id (str): The ID of the execution to update.
        payload (dict): Fields to update in the execution.

    Returns:
        dict: Status and updated execution details.
    """
    try:
        execution = execution_db.get_item({"id": id})
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
                    "Cannot update the project once the execution is started",
                ),
            )

        updated_execution = Execution(
            id=execution["id"],
            config=payload,
            gt_data=payload.get("prestep", {}).get("gt_data", execution["gt_data"]),
            kb_data=payload.get("prestep", {}).get("kb_data", execution["kb_data"]),
            region=payload.get("prestep", {}).get("region", execution["region"]),
            name=payload["name"]
        )
        execution_db.put_item(updated_execution.dict())

        return {
            "status": "success",
            "message": "Execution updated successfully.",
            "updated_execution": updated_execution.dict()
        }
    except HTTPException as http_exc:
        # Re-raise the HTTPException with the same status code and detail
        raise http_exc
    except Exception as e:
        logger.error(f"Failed to update the execution: {str(e)}")
        raise HTTPException(
            status_code=StatusCodes.INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                ErrorTypes.SERVER_ERROR,
                "An issue occurred while updating the project. Please contact admin",
            ),
        )

@router.post("/execution/{execution_id}/execute")
async def execute_experiments(
        execution_id: str,
        execution_db=Depends(get_execution_db),
        orchestrator=Depends(get_step_function_orchestrator)
):
    """
    Trigger the orchestration process for the given execution ID.

    Args:
        execution_id (str): The execution ID.

    Returns:
        A success message if orchestration is started.
    """
    try:
        in_progress = execution_db.scan(
            filter_expression="#status = :status",
            expression_values={":status": "in_progress"},
            expression_attribute_names={"#status": "status"}
        )

        in_progress_items = in_progress.get("Items", [])
        if in_progress_items:
            # Fetch the first in-progress item
            in_progress_item = in_progress_items[0]

            # Raise an HTTPException with a detailed error message
            raise HTTPException(
                status_code=StatusCodes.BAD_REQUEST,
                detail=create_error_response(
                    ErrorTypes.VALIDATION_ERROR,
                    f"Another project '{in_progress_item['name']}' execution is currently in progress. Please wait until it completes.",
                ),
            )
        execution = execution_db.get_item({"id": execution_id})
        if not execution:
            raise HTTPException(
                status_code=StatusCodes.BAD_REQUEST,
                detail=create_error_response(
                    ErrorTypes.VALIDATION_ERROR,
                    "No project found for the provided ID",
                ),
            )
        
        response = orchestrator.run_experiment_orchestration(execution_id)
       
        execution["status"] = "in_progress"
        execution_db.put_item(execution)

        return {
            "status": "success",
            "message": f"Orchestration started for execution ID {execution_id}",
            "execution_arn": response['executionArn']
        }
    except HTTPException as http_exc:
        # Re-raise the HTTPException with the same status code and detail
        raise http_exc
    except Exception as e:
        logger.error(f"Failed to trigger the execution: {str(e)}")
        raise HTTPException(
            status_code=StatusCodes.INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                ErrorTypes.SERVER_ERROR,
                "An issue occurred when triggering the execution of the project. Please contact admin",
            ),
        )

@router.get("/execution/{execution_id}/valid_experiment")
async def generate_config(
        execution_id: str,
        execution_db=Depends(get_execution_db)
):
    """
    Generate all possible valid experiment configurations for a given execution ID.
    """
    try:
        execution = execution_db.get_item({"id": execution_id})
        if not execution:
            raise HTTPException(
                status_code=StatusCodes.BAD_REQUEST,
                detail=create_error_response(
                    ErrorTypes.VALIDATION_ERROR,
                    "No project found for the provided ID",
                ),
            )
        parameter_options = execution.get('config')
        combinations = await asyncio.to_thread(generate_all_combinations, parameter_options)
        return combinations
    except HTTPException as http_exc:
        # Re-raise the HTTPException with the same status code and detail
        raise http_exc
    except Exception as e:
        logger.error(f"Failed to generate valid experiments: {str(e)}")
        raise HTTPException(
            status_code=StatusCodes.INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                ErrorTypes.SERVER_ERROR,
                "Failed to generate valid experiments. Please contact admin",
            ),
        )
