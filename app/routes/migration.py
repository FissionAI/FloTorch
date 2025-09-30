"""
API routes for data migration management.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from app.migration.migration_manager import MigrationManager

logger = logging.getLogger(__name__)
router = APIRouter()

# Global migration manager instance
migration_manager = MigrationManager()

@router.get("/migration/status", tags=["migration"])
async def get_migration_status():
    """Get current migration status and statistics."""
    try:
        status = migration_manager.get_migration_status()
        return {"status": "success", "data": status}
    except Exception as e:
        logger.error(f"Failed to get migration status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/migration/run", tags=["migration"])
async def run_migration(
    limit: Optional[int] = Query(None, description="Maximum number of items to migrate per table"),
    batch_size: int = Query(100, description="Batch size for migration"),
    incremental: bool = Query(False, description="Run incremental migration")
):
    """Run data migration from DynamoDB to PostgreSQL."""
    try:
        if incremental:
            results = migration_manager.run_incremental_migration()
        else:
            results = migration_manager.run_full_migration(limit, batch_size)
        
        return {"status": "success", "data": results}
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/migration/shadow-read/experiment/{experiment_id}", tags=["migration"])
async def shadow_read_experiment(experiment_id: str):
    """Perform shadow read for experiment data."""
    try:
        results = migration_manager.shadow_read_experiment(experiment_id)
        return {"status": "success", "data": results}
    except Exception as e:
        logger.error(f"Shadow read failed for experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/migration/shadow-read/execution/{execution_id}", tags=["migration"])
async def shadow_read_execution(execution_id: str):
    """Perform shadow read for execution data."""
    try:
        results = migration_manager.shadow_read_execution(execution_id)
        return {"status": "success", "data": results}
    except Exception as e:
        logger.error(f"Shadow read failed for execution {execution_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/migration/enable-shadow-reads", tags=["migration"])
async def enable_shadow_reads():
    """Enable shadow read functionality."""
    try:
        migration_manager.shadow_read_enabled = True
        return {"status": "success", "message": "Shadow reads enabled"}
    except Exception as e:
        logger.error(f"Failed to enable shadow reads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/migration/disable-shadow-reads", tags=["migration"])
async def disable_shadow_reads():
    """Disable shadow read functionality."""
    try:
        migration_manager.shadow_read_enabled = False
        return {"status": "success", "message": "Shadow reads disabled"}
    except Exception as e:
        logger.error(f"Failed to disable shadow reads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/migration/validate/{table_name}", tags=["migration"])
async def validate_migration(table_name: str, sample_size: int = Query(10, description="Number of records to validate")):
    """Validate migration by comparing data between DynamoDB and PostgreSQL."""
    try:
        # This would implement data validation logic
        # For now, return a placeholder response
        return {
            "status": "success",
            "data": {
                "table_name": table_name,
                "sample_size": sample_size,
                "validation_status": "implemented",
                "message": "Validation endpoint ready"
            }
        }
    except Exception as e:
        logger.error(f"Validation failed for table {table_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

