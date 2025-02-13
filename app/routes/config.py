from fastapi import APIRouter
from util.open_search_config_utils import OpenSearchUtils

router = APIRouter()

@router.get("/config", tags=["config"])
async def config():
    return {
        "opensearch": OpenSearchUtils.opensearch_config()
    }
