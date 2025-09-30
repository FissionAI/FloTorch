"""
Data migration service for migrating from DynamoDB to PostgreSQL.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from sqlalchemy.orm import Session
from app.database.connection import db_manager
from app.database.models import Experiment, Execution, QuestionMetrics, ModelInvocations
import boto3

logger = logging.getLogger(__name__)

class DataMigrator:
    """
    Service for migrating data from DynamoDB to PostgreSQL.
    Supports both full migration and incremental sync.
    """
    
    def __init__(self, aws_region: str = "us-east-1"):
        self.aws_region = aws_region
        self.dynamodb_clients = {}
        self._init_dynamodb_clients()
    
    def _init_dynamodb_clients(self):
        """Initialize DynamoDB clients for each table."""
        table_configs = {
            "experiments": os.getenv("experiment_table", "flotorch_experiment"),
            "executions": os.getenv("execution_table", "flotorch_execution"),
            "question_metrics": os.getenv("experiment_question_metrics_table", "flotorch_question_metrics"),
            "model_invocations": os.getenv("execution_model_invocations_table", "flotorch_model_invocations")
        }
        
        for table_name, dynamodb_table in table_configs.items():
            if not dynamodb_table:
                continue
            # Lightweight boto3-based wrapper providing .table with needed methods
            ddb_client = boto3.client("dynamodb", region_name=self.aws_region)

            class _TableWrapper:
                def __init__(self, client, table_name):
                    self._client = client
                    self._name = table_name
                def scan(self, **kwargs):
                    return self._client.scan(TableName=self._name, **kwargs)
                def get_item(self, **kwargs):
                    return self._client.get_item(TableName=self._name, **kwargs)

            class _DynAdapter:
                def __init__(self, client, table_name):
                    self.table = _TableWrapper(client, table_name)

            self.dynamodb_clients[table_name] = _DynAdapter(ddb_client, dynamodb_table)
            logger.info(f"Initialized DynamoDB client for {table_name} -> {dynamodb_table}")
    
    def migrate_experiments(self, limit: Optional[int] = None, batch_size: int = 100) -> Dict[str, Any]:
        """Migrate experiments from DynamoDB to PostgreSQL."""
        logger.info("Starting experiments migration...")
        
        try:
            dynamodb_client = self.dynamodb_clients.get("experiments")
            if not dynamodb_client:
                logger.warning("No DynamoDB client for experiments, skipping migration")
                return {"status": "skipped", "reason": "no_dynamodb_client"}
            
            # Scan DynamoDB table
            items = self._scan_dynamodb_table(dynamodb_client, limit, batch_size)
            logger.info(f"Found {len(items)} experiments to migrate")
            
            migrated_count = 0
            failed_count = 0
            
            with db_manager.get_session() as session:
                for item in items:
                    try:
                        # Transform DynamoDB item to PostgreSQL model
                        experiment_data = self._transform_experiment_item(item)
                        
                        # Check if experiment already exists
                        existing = session.query(Experiment).filter_by(
                            experiment_id=experiment_data["experiment_id"]
                        ).first()
                        
                        if existing:
                            logger.debug(f"Experiment {experiment_data['experiment_id']} already exists, skipping")
                            continue
                        
                        # Create new experiment
                        experiment = Experiment(**experiment_data)
                        session.add(experiment)
                        migrated_count += 1
                        
                        if migrated_count % batch_size == 0:
                            session.commit()
                            logger.info(f"Migrated {migrated_count} experiments...")
                    
                    except Exception as e:
                        logger.error(f"Failed to migrate experiment {item.get('experiment_id', 'unknown')}: {e}")
                        failed_count += 1
                        session.rollback()
                
                session.commit()
            
            result = {
                "status": "completed",
                "migrated_count": migrated_count,
                "failed_count": failed_count,
                "total_found": len(items)
            }
            
            logger.info(f"Experiments migration completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Experiments migration failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def migrate_executions(self, limit: Optional[int] = None, batch_size: int = 100) -> Dict[str, Any]:
        """Migrate executions from DynamoDB to PostgreSQL."""
        logger.info("Starting executions migration...")
        
        try:
            dynamodb_client = self.dynamodb_clients.get("executions")
            if not dynamodb_client:
                logger.warning("No DynamoDB client for executions, skipping migration")
                return {"status": "skipped", "reason": "no_dynamodb_client"}
            
            items = self._scan_dynamodb_table(dynamodb_client, limit, batch_size)
            logger.info(f"Found {len(items)} executions to migrate")
            
            migrated_count = 0
            failed_count = 0
            
            with db_manager.get_session() as session:
                for item in items:
                    try:
                        execution_data = self._transform_execution_item(item)
                        
                        existing = session.query(Execution).filter_by(
                            execution_id=execution_data["execution_id"]
                        ).first()
                        
                        if existing:
                            continue
                        
                        execution = Execution(**execution_data)
                        session.add(execution)
                        migrated_count += 1
                        
                        if migrated_count % batch_size == 0:
                            session.commit()
                            logger.info(f"Migrated {migrated_count} executions...")
                    
                    except Exception as e:
                        logger.error(f"Failed to migrate execution {item.get('execution_id', 'unknown')}: {e}")
                        failed_count += 1
                        session.rollback()
                
                session.commit()
            
            result = {
                "status": "completed",
                "migrated_count": migrated_count,
                "failed_count": failed_count,
                "total_found": len(items)
            }
            
            logger.info(f"Executions migration completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Executions migration failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def migrate_question_metrics(self, limit: Optional[int] = None, batch_size: int = 100) -> Dict[str, Any]:
        """Migrate question metrics from DynamoDB to PostgreSQL."""
        logger.info("Starting question metrics migration...")
        
        try:
            dynamodb_client = self.dynamodb_clients.get("question_metrics")
            if not dynamodb_client:
                logger.warning("No DynamoDB client for question metrics, skipping migration")
                return {"status": "skipped", "reason": "no_dynamodb_client"}
            
            items = self._scan_dynamodb_table(dynamodb_client, limit, batch_size)
            logger.info(f"Found {len(items)} question metrics to migrate")
            
            migrated_count = 0
            failed_count = 0
            
            with db_manager.get_session() as session:
                for item in items:
                    try:
                        metrics_data = self._transform_question_metrics_item(item)
                        
                        # Use composite key for uniqueness
                        existing = session.query(QuestionMetrics).filter_by(
                            experiment_id=metrics_data["experiment_id"],
                            execution_id=metrics_data["execution_id"],
                            question_id=metrics_data["question_id"]
                        ).first()
                        
                        if existing:
                            continue
                        
                        metrics = QuestionMetrics(**metrics_data)
                        session.add(metrics)
                        migrated_count += 1
                        
                        if migrated_count % batch_size == 0:
                            session.commit()
                            logger.info(f"Migrated {migrated_count} question metrics...")
                    
                    except Exception as e:
                        logger.error(f"Failed to migrate question metrics {item.get('question_id', 'unknown')}: {e}")
                        failed_count += 1
                        session.rollback()
                
                session.commit()
            
            result = {
                "status": "completed",
                "migrated_count": migrated_count,
                "failed_count": failed_count,
                "total_found": len(items)
            }
            
            logger.info(f"Question metrics migration completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Question metrics migration failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def migrate_all(self, limit: Optional[int] = None, batch_size: int = 100) -> Dict[str, Any]:
        """Migrate all tables from DynamoDB to PostgreSQL."""
        logger.info("Starting full data migration...")
        
        results = {}
        
        # Migrate in order of dependencies
        results["experiments"] = self.migrate_experiments(limit, batch_size)
        results["executions"] = self.migrate_executions(limit, batch_size)
        results["question_metrics"] = self.migrate_question_metrics(limit, batch_size)
        
        # Summary
        total_migrated = sum(r.get("migrated_count", 0) for r in results.values() if r.get("status") == "completed")
        total_failed = sum(r.get("failed_count", 0) for r in results.values() if r.get("status") == "completed")
        
        results["summary"] = {
            "total_migrated": total_migrated,
            "total_failed": total_failed,
            "migration_status": "completed" if total_failed == 0 else "completed_with_errors"
        }
        
        logger.info(f"Full migration completed: {results['summary']}")
        return results
    
    def _scan_dynamodb_table(self, dynamodb_client, limit: Optional[int] = None, batch_size: int = 100) -> List[Dict[str, Any]]:
        """Scan DynamoDB table and return all items."""
        items = []
        last_evaluated_key = None
        
        while True:
            scan_params = {
                "Limit": min(batch_size, limit or batch_size)
            }
            
            if last_evaluated_key:
                scan_params["ExclusiveStartKey"] = last_evaluated_key
            
            response = dynamodb_client.table.scan(**scan_params)
            items.extend(response.get("Items", []))
            
            last_evaluated_key = response.get("LastEvaluatedKey")
            
            if not last_evaluated_key or (limit and len(items) >= limit):
                break
        
        return items[:limit] if limit else items
    
    def _transform_experiment_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Transform DynamoDB experiment item to PostgreSQL format."""
        return {
            "experiment_id": item.get("experiment_id", {}).get("S"),
            "experiment_name": item.get("experiment_name", {}).get("S", ""),
            "description": item.get("description", {}).get("S"),
            "status": item.get("status", {}).get("S", "created"),
            "aws_region": item.get("aws_region", {}).get("S"),
            "s3_bucket": item.get("s3_bucket", {}).get("S"),
            "opensearch_host": item.get("opensearch_host", {}).get("S"),
            "opensearch_serverless": item.get("opensearch_serverless", {}).get("BOOL", False),
            "chunking_algorithm": item.get("chunking_algorithm", {}).get("S"),
            "embedding_model": item.get("embedding_model", {}).get("S"),
            "inference_model": item.get("inference_model", {}).get("S"),
            "indexing_algorithm": item.get("indexing_algorithm", {}).get("S"),
            "metadata": self._extract_metadata(item),
            "created_at": self._parse_datetime(item.get("created_at", {}).get("S")),
            "updated_at": self._parse_datetime(item.get("updated_at", {}).get("S"))
        }
    
    def _transform_execution_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Transform DynamoDB execution item to PostgreSQL format."""
        return {
            "execution_id": item.get("execution_id", {}).get("S"),
            "experiment_id": item.get("experiment_id", {}).get("S"),
            "execution_name": item.get("execution_name", {}).get("S"),
            "status": item.get("status", {}).get("S", "pending"),
            "started_at": self._parse_datetime(item.get("started_at", {}).get("S")),
            "completed_at": self._parse_datetime(item.get("completed_at", {}).get("S")),
            "step_function_arn": item.get("step_function_arn", {}).get("S"),
            "step_function_execution_arn": item.get("step_function_execution_arn", {}).get("S"),
            "total_questions": int(item.get("total_questions", {}).get("N", "0")),
            "completed_questions": int(item.get("completed_questions", {}).get("N", "0")),
            "failed_questions": int(item.get("failed_questions", {}).get("N", "0")),
            "metadata": self._extract_metadata(item),
            "created_at": self._parse_datetime(item.get("created_at", {}).get("S")),
            "updated_at": self._parse_datetime(item.get("updated_at", {}).get("S"))
        }
    
    def _transform_question_metrics_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Transform DynamoDB question metrics item to PostgreSQL format."""
        return {
            "experiment_id": item.get("experiment_id", {}).get("S"),
            "execution_id": item.get("execution_id", {}).get("S"),
            "question_id": item.get("question_id", {}).get("S"),
            "question": item.get("question", {}).get("S", ""),
            "ground_truth_answer": item.get("ground_truth_answer", {}).get("S"),
            "generated_answer": item.get("generated_answer", {}).get("S"),
            "answer_accuracy": self._parse_float(item.get("answer_accuracy", {}).get("N")),
            "answer_relevance": self._parse_float(item.get("answer_relevance", {}).get("N")),
            "answer_coherence": self._parse_float(item.get("answer_coherence", {}).get("N")),
            "answer_fluency": self._parse_float(item.get("answer_fluency", {}).get("N")),
            "overall_score": self._parse_float(item.get("overall_score", {}).get("N")),
            "retrieval_time": self._parse_float(item.get("retrieval_time", {}).get("N")),
            "generation_time": self._parse_float(item.get("generation_time", {}).get("N")),
            "total_time": self._parse_float(item.get("total_time", {}).get("N")),
            "input_tokens": int(item.get("input_tokens", {}).get("N", "0")),
            "output_tokens": int(item.get("output_tokens", {}).get("N", "0")),
            "estimated_cost": self._parse_float(item.get("estimated_cost", {}).get("N")),
            "status": item.get("status", {}).get("S", "pending"),
            "error_message": item.get("error_message", {}).get("S"),
            "metadata": self._extract_metadata(item),
            "created_at": self._parse_datetime(item.get("created_at", {}).get("S")),
            "updated_at": self._parse_datetime(item.get("updated_at", {}).get("S"))
        }
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from DynamoDB format."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    def _parse_float(self, value: Optional[str]) -> Optional[float]:
        """Parse float value from DynamoDB format."""
        if not value:
            return None
        try:
            return float(value)
        except:
            return None
    
    def _extract_metadata(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract metadata from DynamoDB item."""
        metadata_fields = ["metadata", "config", "settings"]
        for field in metadata_fields:
            if field in item:
                metadata_item = item[field]
                if "S" in metadata_item:
                    try:
                        return json.loads(metadata_item["S"])
                    except:
                        return {"raw": metadata_item["S"]}
                elif "M" in metadata_item:
                    return self._convert_dynamodb_map(metadata_item["M"])
        return None
    
    def _convert_dynamodb_map(self, dynamodb_map: Dict[str, Any]) -> Dict[str, Any]:
        """Convert DynamoDB map to regular dictionary."""
        result = {}
        for key, value in dynamodb_map.items():
            if "S" in value:
                result[key] = value["S"]
            elif "N" in value:
                result[key] = float(value["N"]) if "." in value["N"] else int(value["N"])
            elif "BOOL" in value:
                result[key] = value["BOOL"]
            elif "M" in value:
                result[key] = self._convert_dynamodb_map(value["M"])
        return result
