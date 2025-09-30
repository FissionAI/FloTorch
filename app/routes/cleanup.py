"""
API routes for managing legacy folder cleanup.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import logging
import os
from app.utils.legacy_cleanup import LegacyCleanup

logger = logging.getLogger(__name__)
router = APIRouter()

# Global cleanup manager instance
cleanup_manager = LegacyCleanup()

@router.get("/cleanup/status", tags=["cleanup"])
async def get_cleanup_status():
    """Get current status of legacy folders and cleanup."""
    try:
        status = cleanup_manager.get_legacy_folder_status()
        return {"status": "success", "data": status}
    except Exception as e:
        logger.error(f"Failed to get cleanup status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup/create-backup", tags=["cleanup"])
async def create_backup():
    """Create backup of legacy folders before removal."""
    try:
        backup_info = cleanup_manager.create_backup()
        return {"status": "success", "data": backup_info}
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup/remove-legacy", tags=["cleanup"])
async def remove_legacy_folders(
    force: bool = Query(False, description="Force removal without backup (dangerous)")
):
    """Remove legacy folders after backup."""
    try:
        removal_info = cleanup_manager.remove_legacy_folders(force=force)
        return {"status": "success", "data": removal_info}
    except Exception as e:
        logger.error(f"Failed to remove legacy folders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup/restore", tags=["cleanup"])
async def restore_from_backup(backup_info: Dict[str, Any]):
    """Restore legacy folders from backup."""
    try:
        restore_info = cleanup_manager.restore_from_backup(backup_info)
        return {"status": "success", "data": restore_info}
    except Exception as e:
        logger.error(f"Failed to restore from backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup/cleanup-backup", tags=["cleanup"])
async def cleanup_backup(backup_info: Dict[str, Any]):
    """Remove backup after successful cleanup."""
    try:
        cleanup_info = cleanup_manager.cleanup_backup(backup_info)
        return {"status": "success", "data": cleanup_info}
    except Exception as e:
        logger.error(f"Failed to cleanup backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup/full-cleanup", tags=["cleanup"])
async def full_cleanup(
    keep_backup: bool = Query(True, description="Keep backup after cleanup")
):
    """Perform full cleanup: backup -> remove -> optionally cleanup backup."""
    try:
        results = {}
        
        # Step 1: Create backup
        logger.info("Step 1: Creating backup...")
        backup_info = cleanup_manager.create_backup()
        results["backup"] = backup_info
        
        # Step 2: Remove legacy folders
        logger.info("Step 2: Removing legacy folders...")
        removal_info = cleanup_manager.remove_legacy_folders()
        results["removal"] = removal_info
        
        # Step 3: Cleanup backup if requested
        if not keep_backup:
            logger.info("Step 3: Cleaning up backup...")
            cleanup_info = cleanup_manager.cleanup_backup(backup_info)
            results["backup_cleanup"] = cleanup_info
        
        return {
            "status": "success",
            "message": "Full cleanup completed successfully",
            "data": results
        }
    except Exception as e:
        logger.error(f"Full cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cleanup/validate-cleanup", tags=["cleanup"])
async def validate_cleanup():
    """Validate that cleanup can be performed safely."""
    try:
        validation = {
            "can_proceed": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check if legacy folders exist
        status = cleanup_manager.get_legacy_folder_status()
        
        if not status["folders_exist"]:
            validation["warnings"].append("No legacy folders found to clean up")
            validation["can_proceed"] = False
        
        # Check if adapters are working
        try:
            from app.adapters.opensearch_adapter import OpenSearchAdapter
            from app.adapters.retriever_adapter import RetrieverAdapter
            from app.adapters.indexer_adapter import IndexerAdapter
            from app.adapters.eval_adapter import EvalAdapter
            validation["recommendations"].append("All adapters are available")
        except ImportError as e:
            validation["errors"].append(f"Adapter import failed: {e}")
            validation["can_proceed"] = False
        
        # Check if external services are configured
        external_services_enabled = (
            os.getenv("USE_EXTERNAL_SERVICES", "false").lower() == "true" or
            os.getenv("USE_FLOTORCH_CORE", "false").lower() == "true"
        )
        
        if not external_services_enabled:
            validation["warnings"].append("External services not enabled - ensure you have fallback mechanisms")
            validation["recommendations"].append("Consider enabling USE_EXTERNAL_SERVICES or USE_FLOTORCH_CORE")
        
        return {"status": "success", "data": validation}
    except Exception as e:
        logger.error(f"Cleanup validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
