"""
API routes for managing database cutover from DynamoDB to PostgreSQL.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import os
import logging
from app.migration.migration_manager import MigrationManager

logger = logging.getLogger(__name__)
router = APIRouter()

# Global migration manager instance
migration_manager = MigrationManager()

@router.post("/cutover/enable-dual-writes", tags=["cutover"])
async def enable_dual_writes():
    """Enable dual writes to both DynamoDB and PostgreSQL."""
    try:
        os.environ["ENABLE_DUAL_WRITES"] = "true"
        return {"status": "success", "message": "Dual writes enabled"}
    except Exception as e:
        logger.error(f"Failed to enable dual writes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cutover/disable-dual-writes", tags=["cutover"])
async def disable_dual_writes():
    """Disable dual writes (PostgreSQL only)."""
    try:
        os.environ["ENABLE_DUAL_WRITES"] = "false"
        return {"status": "success", "message": "Dual writes disabled"}
    except Exception as e:
        logger.error(f"Failed to disable dual writes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cutover/enable-postgres-reads", tags=["cutover"])
async def enable_postgres_reads():
    """Enable reads from PostgreSQL instead of DynamoDB."""
    try:
        os.environ["READ_FROM_POSTGRES"] = "true"
        return {"status": "success", "message": "PostgreSQL reads enabled"}
    except Exception as e:
        logger.error(f"Failed to enable PostgreSQL reads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cutover/disable-postgres-reads", tags=["cutover"])
async def disable_postgres_reads():
    """Disable PostgreSQL reads (DynamoDB reads only)."""
    try:
        os.environ["READ_FROM_POSTGRES"] = "false"
        return {"status": "success", "message": "PostgreSQL reads disabled"}
    except Exception as e:
        logger.error(f"Failed to disable PostgreSQL reads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cutover/status", tags=["cutover"])
async def get_cutover_status():
    """Get current cutover status and configuration."""
    try:
        status = {
            "dual_writes_enabled": os.getenv("ENABLE_DUAL_WRITES", "false").lower() == "true",
            "read_from_postgres": os.getenv("READ_FROM_POSTGRES", "false").lower() == "true",
            "db_type": os.getenv("DB_TYPE", "DYNAMODB"),
            "shadow_reads_enabled": os.getenv("ENABLE_SHADOW_READS", "false").lower() == "true"
        }
        
        # Get migration status
        migration_status = migration_manager.get_migration_status()
        status.update(migration_status)
        
        return {"status": "success", "data": status}
    except Exception as e:
        logger.error(f"Failed to get cutover status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cutover/validate-data-consistency", tags=["cutover"])
async def validate_data_consistency(
    sample_size: int = Query(10, description="Number of records to validate per table")
):
    """Validate data consistency between DynamoDB and PostgreSQL."""
    try:
        results = {}
        
        # Validate experiments
        experiments_pg = migration_manager._get_postgresql_count("experiments")
        experiments_ddb = migration_manager._get_dynamodb_count("experiments")
        
        results["experiments"] = {
            "postgresql_count": experiments_pg,
            "dynamodb_count": experiments_ddb,
            "consistent": experiments_pg == experiments_ddb
        }
        
        # Validate executions
        executions_pg = migration_manager._get_postgresql_count("executions")
        executions_ddb = migration_manager._get_dynamodb_count("executions")
        
        results["executions"] = {
            "postgresql_count": executions_pg,
            "dynamodb_count": executions_ddb,
            "consistent": executions_pg == executions_ddb
        }
        
        # Validate question metrics
        metrics_pg = migration_manager._get_postgresql_count("question_metrics")
        metrics_ddb = migration_manager._get_dynamodb_count("question_metrics")
        
        results["question_metrics"] = {
            "postgresql_count": metrics_pg,
            "dynamodb_count": metrics_ddb,
            "consistent": metrics_pg == metrics_ddb
        }
        
        # Overall consistency
        all_consistent = all(
            table_result["consistent"] 
            for table_result in results.values()
        )
        
        results["overall"] = {
            "consistent": all_consistent,
            "validation_timestamp": migration_manager._get_current_timestamp()
        }
        
        return {"status": "success", "data": results}
    except Exception as e:
        logger.error(f"Data consistency validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cutover/run-full-cutover", tags=["cutover"])
async def run_full_cutover():
    """Run full cutover to PostgreSQL (enable reads, disable dual writes)."""
    try:
        # Step 1: Enable PostgreSQL reads
        os.environ["READ_FROM_POSTGRES"] = "true"
        
        # Step 2: Disable dual writes
        os.environ["ENABLE_DUAL_WRITES"] = "false"
        
        # Step 3: Update DB_TYPE to PostgreSQL
        os.environ["DB_TYPE"] = "POSTGRESDB"
        
        return {
            "status": "success",
            "message": "Full cutover to PostgreSQL completed",
            "changes": {
                "read_from_postgres": True,
                "dual_writes_enabled": False,
                "db_type": "POSTGRESDB"
            }
        }
    except Exception as e:
        logger.error(f"Full cutover failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cutover/rollback-to-dynamodb", tags=["cutover"])
async def rollback_to_dynamodb():
    """Rollback to DynamoDB (disable PostgreSQL reads, enable DynamoDB)."""
    try:
        # Step 1: Disable PostgreSQL reads
        os.environ["READ_FROM_POSTGRES"] = "false"
        
        # Step 2: Disable dual writes
        os.environ["ENABLE_DUAL_WRITES"] = "false"
        
        # Step 3: Update DB_TYPE to DynamoDB
        os.environ["DB_TYPE"] = "DYNAMODB"
        
        return {
            "status": "success",
            "message": "Rollback to DynamoDB completed",
            "changes": {
                "read_from_postgres": False,
                "dual_writes_enabled": False,
                "db_type": "DYNAMODB"
            }
        }
    except Exception as e:
        logger.error(f"Rollback to DynamoDB failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cutover/health-check", tags=["cutover"])
async def cutover_health_check():
    """Perform health check for both databases."""
    try:
        health_status = {
            "postgresql": {"status": "unknown", "error": None},
            "dynamodb": {"status": "unknown", "error": None},
            "timestamp": migration_manager._get_current_timestamp()
        }
        
        # Check PostgreSQL health
        try:
            pg_count = migration_manager._get_postgresql_count("experiments")
            health_status["postgresql"] = {"status": "healthy", "count": pg_count}
        except Exception as e:
            health_status["postgresql"] = {"status": "unhealthy", "error": str(e)}
        
        # Check DynamoDB health
        try:
            ddb_count = migration_manager._get_dynamodb_count("experiments")
            health_status["dynamodb"] = {"status": "healthy", "count": ddb_count}
        except Exception as e:
            health_status["dynamodb"] = {"status": "unhealthy", "error": str(e)}
        
        # Overall health
        all_healthy = all(
            db["status"] == "healthy" 
            for db in health_status.values() 
            if isinstance(db, dict) and "status" in db
        )
        
        health_status["overall"] = {"status": "healthy" if all_healthy else "unhealthy"}
        
        return {"status": "success", "data": health_status}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

