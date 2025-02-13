from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/config/opensearch", tags=["opensearch config"])
async def opensearch_config():
    opensearch_endpoint = os.getenv("OPENSEARCH_ENDPOINT")
    configured = bool(opensearch_endpoint)  # True if string is not empty/None, otherwise False.
    return {"status": {"configured": configured}}
