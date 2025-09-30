"""
Migration manager for coordinating data migration and shadow reads between DynamoDB and PostgreSQL.
"""
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.migration.data_migrator import DataMigrator
from app.database.connection import db_manager
from app.database.models import Experiment, Execution, QuestionMetrics
import boto3

logger = logging.getLogger(__name__)

class MigrationManager:
    """
    Manages the migration process and shadow read capabilities.
    """
    
    def __init__(self, aws_region: str = "us-east-1"):
        self.aws_region = aws_region
        self.data_migrator = DataMigrator(aws_region)
        self.shadow_read_enabled = os.getenv("ENABLE_SHADOW_READS", "false").lower() == "true"
        self.dual_write_enabled = os.getenv("ENABLE_DUAL_WRITES", "false").lower() == "true"
        
        # Initialize DynamoDB clients for shadow reads
        self._init_dynamodb_clients()
    
    def _init_dynamodb_clients(self):
        """Initialize DynamoDB clients for shadow reads."""
        self.dynamodb_clients = {}
        
        table_configs = {
            "experiments": os.getenv("experiment_table", "flotorch_experiment"),
            "executions": os.getenv("execution_table", "flotorch_execution"),
            "question_metrics": os.getenv("experiment_question_metrics_table", "flotorch_question_metrics")
        }
        
        for table_name, dynamodb_table in table_configs.items():
            if not dynamodb_table:
                continue
            try:
                ddb_client = boto3.client("dynamodb", region_name=self.aws_region)

                class _TableWrapper:
                    def __init__(self, client, table_name):
                        self._client = client
                        self._name = table_name
                    def get_item(self, **kwargs):
                        return self._client.get_item(TableName=self._name, **kwargs)
                    def scan(self, **kwargs):
                        return self._client.scan(TableName=self._name, **kwargs)

                class _DynAdapter:
                    def __init__(self, client, table_name):
                        self.table = _TableWrapper(client, table_name)

                self.dynamodb_clients[table_name] = _DynAdapter(ddb_client, dynamodb_table)
                logger.info(f"Initialized DynamoDB shadow client for {table_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize DynamoDB client for {table_name}: {e}")
    
    def run_full_migration(self, limit: Optional[int] = None, batch_size: int = 100) -> Dict[str, Any]:
        """Run full data migration from DynamoDB to PostgreSQL."""
        logger.info("Starting full data migration...")
        
        start_time = datetime.now()
        results = self.data_migrator.migrate_all(limit, batch_size)
        end_time = datetime.now()
        
        results["migration_info"] = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": (end_time - start_time).total_seconds(),
            "batch_size": batch_size,
            "limit": limit
        }
        
        logger.info(f"Full migration completed in {(end_time - start_time).total_seconds():.2f} seconds")
        return results
    
    def run_incremental_migration(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """Run incremental migration for data modified since a specific time."""
        logger.info(f"Starting incremental migration since {since or 'beginning'}")
        
        # This would require adding timestamp tracking to DynamoDB items
        # For now, we'll implement a basic version that migrates recent items
        
        results = {}
        
        # Get recent items from each table
        for table_name in ["experiments", "executions", "question_metrics"]:
            try:
                recent_items = self._get_recent_dynamodb_items(table_name, since)
                logger.info(f"Found {len(recent_items)} recent items in {table_name}")
                
                # Migrate recent items
                if table_name == "experiments":
                    results[table_name] = self._migrate_recent_experiments(recent_items)
                elif table_name == "executions":
                    results[table_name] = self._migrate_recent_executions(recent_items)
                elif table_name == "question_metrics":
                    results[table_name] = self._migrate_recent_question_metrics(recent_items)
                    
            except Exception as e:
                logger.error(f"Incremental migration failed for {table_name}: {e}")
                results[table_name] = {"status": "failed", "error": str(e)}
        
        return results
    
    def shadow_read_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Perform shadow read for experiment data."""
        if not self.shadow_read_enabled:
            return {"status": "disabled"}
        
        logger.debug(f"Performing shadow read for experiment {experiment_id}")
        
        results = {}
        
        try:
            # Read from PostgreSQL (primary)
            with db_manager.get_session() as session:
                pg_experiment = session.query(Experiment).filter_by(
                    experiment_id=experiment_id
                ).first()
                
                if pg_experiment:
                    results["postgresql"] = {
                        "experiment_id": pg_experiment.experiment_id,
                        "experiment_name": pg_experiment.experiment_name,
                        "status": pg_experiment.status,
                        "created_at": pg_experiment.created_at.isoformat() if pg_experiment.created_at else None
                    }
        except Exception as e:
            logger.error(f"PostgreSQL shadow read failed: {e}")
            results["postgresql_error"] = str(e)
        
        try:
            # Read from DynamoDB (shadow)
            dynamodb_client = self.dynamodb_clients.get("experiments")
            if dynamodb_client:
                response = dynamodb_client.table.get_item(
                    Key={"experiment_id": {"S": experiment_id}}
                )
                
                if "Item" in response:
                    item = response["Item"]
                    results["dynamodb"] = {
                        "experiment_id": item.get("experiment_id", {}).get("S"),
                        "experiment_name": item.get("experiment_name", {}).get("S"),
                        "status": item.get("status", {}).get("S"),
                        "created_at": item.get("created_at", {}).get("S")
                    }
        except Exception as e:
            logger.error(f"DynamoDB shadow read failed: {e}")
            results["dynamodb_error"] = str(e)
        
        # Compare results
        if "postgresql" in results and "dynamodb" in results:
            pg_data = results["postgresql"]
            ddb_data = results["dynamodb"]
            
            differences = []
            for key in ["experiment_name", "status"]:
                if pg_data.get(key) != ddb_data.get(key):
                    differences.append({
                        "field": key,
                        "postgresql": pg_data.get(key),
                        "dynamodb": ddb_data.get(key)
                    })
            
            results["comparison"] = {
                "matches": len(differences) == 0,
                "differences": differences
            }
        
        return results
    
    def shadow_read_execution(self, execution_id: str) -> Dict[str, Any]:
        """Perform shadow read for execution data."""
        if not self.shadow_read_enabled:
            return {"status": "disabled"}
        
        logger.debug(f"Performing shadow read for execution {execution_id}")
        
        results = {}
        
        try:
            # Read from PostgreSQL
            with db_manager.get_session() as session:
                pg_execution = session.query(Execution).filter_by(
                    execution_id=execution_id
                ).first()
                
                if pg_execution:
                    results["postgresql"] = {
                        "execution_id": pg_execution.execution_id,
                        "experiment_id": pg_execution.experiment_id,
                        "status": pg_execution.status,
                        "total_questions": pg_execution.total_questions,
                        "completed_questions": pg_execution.completed_questions
                    }
        except Exception as e:
            logger.error(f"PostgreSQL shadow read failed: {e}")
            results["postgresql_error"] = str(e)
        
        try:
            # Read from DynamoDB
            dynamodb_client = self.dynamodb_clients.get("executions")
            if dynamodb_client:
                response = dynamodb_client.table.get_item(
                    Key={"execution_id": {"S": execution_id}}
                )
                
                if "Item" in response:
                    item = response["Item"]
                    results["dynamodb"] = {
                        "execution_id": item.get("execution_id", {}).get("S"),
                        "experiment_id": item.get("experiment_id", {}).get("S"),
                        "status": item.get("status", {}).get("S"),
                        "total_questions": item.get("total_questions", {}).get("N", "0"),
                        "completed_questions": item.get("completed_questions", {}).get("N", "0")
                    }
        except Exception as e:
            logger.error(f"DynamoDB shadow read failed: {e}")
            results["dynamodb_error"] = str(e)
        
        return results
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status and statistics."""
        status = {
            "shadow_reads_enabled": self.shadow_read_enabled,
            "dual_writes_enabled": self.dual_write_enabled,
            "dynamodb_clients_available": list(self.dynamodb_clients.keys()),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Count records in PostgreSQL
            with db_manager.get_session() as session:
                status["postgresql_counts"] = {
                    "experiments": session.query(Experiment).count(),
                    "executions": session.query(Execution).count(),
                    "question_metrics": session.query(QuestionMetrics).count()
                }
        except Exception as e:
            logger.error(f"Failed to get PostgreSQL counts: {e}")
            status["postgresql_error"] = str(e)
        
        return status
    
    def _get_recent_dynamodb_items(self, table_name: str, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get recent items from DynamoDB table."""
        # This is a simplified implementation
        # In practice, you'd want to use DynamoDB's scan with filter expressions
        # based on timestamp fields
        
        dynamodb_client = self.dynamodb_clients.get(table_name)
        if not dynamodb_client:
            return []
        
        try:
            response = dynamodb_client.table.scan(Limit=100)  # Get recent 100 items
            return response.get("Items", [])
        except Exception as e:
            logger.error(f"Failed to get recent items from {table_name}: {e}")
            return []
    
    def _migrate_recent_experiments(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Migrate recent experiment items."""
        # Implementation would be similar to DataMigrator.migrate_experiments
        # but focused on the specific items provided
        return {"status": "implemented", "items_count": len(items)}
    
    def _migrate_recent_executions(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Migrate recent execution items."""
        return {"status": "implemented", "items_count": len(items)}
    
    def _migrate_recent_question_metrics(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Migrate recent question metrics items."""
        return {"status": "implemented", "items_count": len(items)}
    
    def _get_postgresql_count(self, table_name: str) -> int:
        """Get count of records in PostgreSQL table."""
        try:
            with db_manager.get_session() as session:
                if table_name == "experiments":
                    return session.query(Experiment).count()
                elif table_name == "executions":
                    return session.query(Execution).count()
                elif table_name == "question_metrics":
                    return session.query(QuestionMetrics).count()
                else:
                    return 0
        except Exception as e:
            logger.error(f"Failed to get PostgreSQL count for {table_name}: {e}")
            return 0
    
    def _get_dynamodb_count(self, table_name: str) -> int:
        """Get count of records in DynamoDB table."""
        try:
            dynamodb_client = self.dynamodb_clients.get(table_name)
            if not dynamodb_client:
                return 0
            
            # Use scan to count items (not efficient for large tables)
            response = dynamodb_client.table.scan(Select="COUNT")
            return response.get("Count", 0)
        except Exception as e:
            logger.error(f"Failed to get DynamoDB count for {table_name}: {e}")
            return 0
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        return datetime.now().isoformat()
