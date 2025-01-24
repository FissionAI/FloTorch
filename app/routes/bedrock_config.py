from fastapi import APIRouter, HTTPException
from util.guard_rails_utils import GuardRailsUtils
from util.bedrock_utils import KnowledgeBaseUtils
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
    
        
@router.get("/bedrock/knowledge_bases", tags=["bedrock"])
async def get_knowledge_bases():

    try:
        valid_kbs = KnowledgeBaseUtils().list_knowledge_bases()
        return valid_kbs
    except Exception as e:
        raise HTTPException(status_code=StatusCodes.INTERNAL_SERVER_ERROR, detail=str(e))