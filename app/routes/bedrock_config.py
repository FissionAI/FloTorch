from fastapi import APIRouter, HTTPException
from util.guard_rails_utils import GuardRailsUtils
from constants import StatusCodes

router = APIRouter()

@router.get("/bedrock/guardrails", tags=["bedrock"])
async def health_check():
    "Endpoint to list Bedrock guardrails."

    try:
        response = GuardRailsUtils.get_bedrock_guardrails()
        return response
    except Exception as e:
        raise HTTPException(status_code=StatusCodes.INTERNAL_SERVER_ERROR, detail=str(e))