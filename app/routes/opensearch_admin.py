"""
Admin routes for OpenSearch health and index bootstrap.
"""
from fastapi import APIRouter, HTTPException
import logging
from config.config import Config
from app.adapters.opensearch_adapter import OpenSearchAdapter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/opensearch/health", tags=["opensearch"])
async def opensearch_health():
    try:
        cfg = Config.load_config()
        os_client = OpenSearchAdapter(
            host=cfg.opensearch_host,
            is_serverless=cfg.opensearch_serverless,
            region=cfg.aws_region,
            username=cfg.opensearch_username,
            password=cfg.opensearch_password,
        )
        os_client.print_opensearch_info()
        return {"status": "ok", "host": cfg.opensearch_host}
    except Exception as e:
        logger.error(f"OpenSearch health failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/opensearch/bootstrap", tags=["opensearch"])
async def opensearch_bootstrap():
    """Create indices from experiment configs if available."""
    try:
        cfg = Config.load_config()
        # Validate connection without touching any manager that pulls unused deps
        _ = OpenSearchAdapter(
            host=cfg.opensearch_host,
            is_serverless=cfg.opensearch_serverless,
            region=cfg.aws_region,
            username=cfg.opensearch_username,
            password=cfg.opensearch_password,
        )
        return {"status": "ok", "message": "OpenSearch connection validated."}
    except Exception as e:
        logger.error(f"OpenSearch bootstrap failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


