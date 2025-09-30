"""
PostgreSQL adapter implementing the DBStorage interface for database-agnostic operations.
"""
import os
import logging
from typing import Dict, Any, List, Optional
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.connection import db_manager
from app.database.models import Experiment, Execution, QuestionMetrics, ModelInvocations

logger = logging.getLogger(__name__)

class PostgresAdapter:
    """
    PostgreSQL adapter that implements database operations compatible with the existing DBStorage interface.
    """
    
    def __init__(self, table_name: str, **kwargs):
        # Normalize legacy logical names (flotorch_*) to app model names
        self.table_name = self._normalize_table_name(table_name)
        self.logger = logging.getLogger(f"{__name__}.{table_name}")
        
        # Map table names to model classes
        self.model_map = {
            "experiments": Experiment,
            "executions": Execution,
            "question_metrics": QuestionMetrics,
            "model_invocations": ModelInvocations
        }
        
        if self.table_name not in self.model_map:
            raise ValueError(f"Unknown table name: {self.table_name}")
        
        self.model_class = self.model_map[self.table_name]

    def _normalize_table_name(self, name: str) -> str:
        mapping = {
            "flotorch_experiment": "experiments",
            "flotorch_execution": "executions",
            "flotorch_question_metrics": "question_metrics",
            "flotorch_model_invocations": "model_invocations",
        }
        return mapping.get(name, name)
    
    def _get_session(self) -> Session:
        """Get database session."""
        return db_manager.SessionLocal()
    
    def create_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new item in the database."""
        try:
            # Legacy compatibility: support simple write() shape used by routes
            if self.table_name == "executions":
                return self._write_execution(item_data)
            if self.table_name == "experiments":
                return self._write_experiment(item_data)

            with db_manager.get_session() as session:
                model_instance = self.model_class(**item_data)
                session.add(model_instance)
                session.flush()

                return self._model_to_dict(model_instance)
        except Exception as e:
            self.logger.error(f"Failed to create item in {self.table_name}: {e}")
            raise
    
    def get_item(self, key: str, value: Any) -> Optional[Dict[str, Any]]:
        """Get an item by key-value pair."""
        try:
            if self.table_name == "executions" and key == "id":
                items = self.read({"id": value})
                return items[0] if items else None
            if self.table_name == "experiments" and key == "id":
                items = self.read({"id": value})
                return items[0] if items else None

            with db_manager.get_session() as session:
                query = session.query(self.model_class)
                if hasattr(self.model_class, key):
                    query = query.filter(getattr(self.model_class, key) == value)
                else:
                    self.logger.warning(f"Key {key} not found in {self.table_name}")
                    return None

                result = query.first()
                if result:
                    return self._model_to_dict(result)
                return None
        except Exception as e:
            self.logger.error(f"Failed to get item from {self.table_name}: {e}")
            raise
    
    def update_item(self, key: str, value: Any, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an item by key-value pair."""
        try:
            if self.table_name == "executions" and key == "id":
                return self._update_execution_by_legacy_id(value, update_data)
            if self.table_name == "experiments" and key == "id":
                return self._update_experiment_by_legacy_id(value, update_data)

            with db_manager.get_session() as session:
                query = session.query(self.model_class)
                if hasattr(self.model_class, key):
                    query = query.filter(getattr(self.model_class, key) == value)
                else:
                    self.logger.warning(f"Key {key} not found in {self.table_name}")
                    return None

                result = query.first()
                if result:
                    for field, new_value in update_data.items():
                        if hasattr(result, field):
                            setattr(result, field, new_value)

                    session.flush()
                    return self._model_to_dict(result)
                return None
        except Exception as e:
            self.logger.error(f"Failed to update item in {self.table_name}: {e}")
            raise
    
    def delete_item(self, key: str, value: Any) -> bool:
        """Delete an item by key-value pair."""
        try:
            with db_manager.get_session() as session:
                query = session.query(self.model_class)
                if hasattr(self.model_class, key):
                    query = query.filter(getattr(self.model_class, key) == value)
                else:
                    self.logger.warning(f"Key {key} not found in {self.table_name}")
                    return False
                
                result = query.first()
                if result:
                    session.delete(result)
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Failed to delete item from {self.table_name}: {e}")
            raise
    
    def query_items(self, filters: Optional[Dict[str, Any]] = None, 
                   limit: Optional[int] = None, 
                   offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Query items with optional filters, limit, and offset."""
        try:
            if self.table_name == "executions":
                return self._read_executions(filters)
            if self.table_name == "experiments":
                return self._read_experiments(filters)

            with db_manager.get_session() as session:
                query = session.query(self.model_class)

                if filters:
                    for field, value in filters.items():
                        if hasattr(self.model_class, field):
                            query = query.filter(getattr(self.model_class, field) == value)

                if limit:
                    query = query.limit(limit)
                if offset:
                    query = query.offset(offset)

                results = query.all()
                return [self._model_to_dict(result) for result in results]
        except Exception as e:
            self.logger.error(f"Failed to query items from {self.table_name}: {e}")
            raise
    
    def _model_to_dict(self, model_instance) -> Dict[str, Any]:
        """Convert SQLAlchemy model instance to dictionary."""
        result = {}
        for column in self.model_class.__table__.columns:
            value = getattr(model_instance, column.name)
            # Handle datetime and UUID serialization
            if hasattr(value, 'isoformat'):  # datetime
                value = value.isoformat()
            elif hasattr(value, 'hex'):  # UUID
                value = str(value)
            result[column.name] = value
        return result

    # --- Legacy DBStorage compatibility layer ---

    # Expected by routes: write(), read(filters_dict | None), update(key_dict, data_dict)
    def write(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.table_name == "executions":
            return self._write_execution(item_data)
        if self.table_name == "experiments":
            return self._write_experiment(item_data)
        return self.create_item(item_data)

    def read(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if self.table_name == "executions":
            return self._read_executions(filters)
        if self.table_name == "experiments":
            return self._read_experiments(filters)
        return self.query_items(filters)

    def update(self, key: Dict[str, Any], data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if self.table_name == "executions" and "id" in key:
            return self._update_execution_by_legacy_id(key["id"], data)
        if self.table_name == "experiments" and "id" in key:
            return self._update_experiment_by_legacy_id(key["id"], data)
        # Fallback: single-key update if matches a column
        if len(key) == 1:
            k, v = next(iter(key.items()))
            return self.update_item(k, v, data)
        self.logger.warning("Complex key updates not supported for this table")
        return None

    def delete(self, key: Dict[str, Any]) -> bool:
        """Legacy delete interface accepting a key dict (e.g., {"id": legacy_id})."""
        try:
            if self.table_name == "experiments" and "id" in key:
                legacy_id = str(key["id"])
                with db_manager.get_session() as session:
                    obj = session.query(Experiment).filter(text("metadata->>'id' = :legacy_id")).params(legacy_id=legacy_id).first()
                    if obj:
                        session.delete(obj)
                        return True
                    # Fallback: try by UUID column if it was a real UUID id
                    try:
                        obj = session.query(Experiment).filter(Experiment.experiment_id == legacy_id).first()
                        if obj:
                            session.delete(obj)
                            return True
                    except Exception:
                        pass
                return False
            if self.table_name == "executions" and "id" in key:
                legacy_id = str(key["id"])
                with db_manager.get_session() as session:
                    obj = session.query(Execution).filter(text("metadata->>'id' = :legacy_id")).params(legacy_id=legacy_id).first()
                    if obj:
                        session.delete(obj)
                        return True
                    try:
                        obj = session.query(Execution).filter(Execution.execution_id == legacy_id).first()
                        if obj:
                            session.delete(obj)
                            return True
                    except Exception:
                        pass
                return False

            # Fallback: single-key delete via mapped column
            if len(key) == 1:
                k, v = next(iter(key.items()))
                return self.delete_item(k, v)

            self.logger.warning("Complex key deletes not supported for this table")
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete item from {self.table_name}: {e}")
            raise

    # --- Execution table legacy helpers ---
    def _write_execution(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store legacy execution payload into PostgreSQL 'executions' table.
        - Uses metadata_json to store opaque fields: id, config, gt_data, kb_data, region, name
        - Stores status into the 'status' column when provided
        - Stores name into 'execution_name' when provided
        Returns a dict compatible with existing routes expectations.
        """
        with db_manager.get_session() as session:
            # Try to find existing by legacy id in metadata_json
            legacy_id = item_data.get("id")
            existing = None
            try:
                existing = session.query(Execution).filter(Execution.metadata_json["id"].astext == str(legacy_id)).first() if legacy_id else None
            except Exception:
                existing = None

            if existing is None:
                model_instance = Execution()
            else:
                model_instance = existing

            # Map fields
            if "name" in item_data:
                model_instance.execution_name = item_data.get("name")
            if "status" in item_data:
                model_instance.status = item_data.get("status")
            # Ensure required FK-like field exists (nullable in practice for legacy flow)
            if getattr(model_instance, "experiment_id", None) is None:
                # Generate a placeholder UUID; experiments are created later in the legacy flow
                model_instance.experiment_id = uuid.uuid4()

            # Merge metadata
            metadata = dict(model_instance.metadata_json or {})
            for key in ["id", "config", "gt_data", "kb_data", "region", "name"]:
                if key in item_data:
                    metadata[key] = item_data[key]
            model_instance.metadata_json = metadata

            session.add(model_instance)
            session.flush()

            return self._execution_to_legacy_dict(model_instance)

    def _read_executions(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        with db_manager.get_session() as session:
            results = session.query(Execution).all()

            def matches_filters(obj: Execution) -> bool:
                if not filters:
                    return True
                # Support filtering by status (column) and by legacy fields in metadata
                for k, v in filters.items():
                    if k == "status" and getattr(obj, "status", None) == v:
                        continue
                    # Check metadata_json
                    md = obj.metadata_json or {}
                    if md.get(k) == v:
                        continue
                    return False
                return True

            filtered = [self._execution_to_legacy_dict(row) for row in results if matches_filters(row)]
            return filtered

    def _update_execution_by_legacy_id(self, legacy_id: Any, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with db_manager.get_session() as session:
            try:
                obj = session.query(Execution).filter(Execution.metadata_json["id"].astext == str(legacy_id)).first()
            except Exception:
                obj = None
            if not obj:
                return None

            # Update mapped columns when relevant
            if "status" in update_data:
                obj.status = update_data["status"]

            # Update metadata
            metadata = dict(obj.metadata_json or {})
            metadata.update(update_data)
            obj.metadata_json = metadata

            session.flush()
            return self._execution_to_legacy_dict(obj)

    def _execution_to_legacy_dict(self, obj: Execution) -> Dict[str, Any]:
        md = obj.metadata_json or {}
        return {
            "id": md.get("id") or (str(obj.execution_id) if hasattr(obj, "execution_id") else None),
            "date": (obj.created_at.isoformat() if hasattr(obj, "created_at") and obj.created_at else None),
            "status": obj.status,
            "validation_status": md.get("validation_status"),
            "gt_data": md.get("gt_data", ""),
            "kb_data": md.get("kb_data", ""),
            "region": md.get("region", ""),
            "config": md.get("config"),
            "name": md.get("name") or getattr(obj, "execution_name", ""),
        }

    # --- Experiment table legacy helpers ---
    def _write_experiment(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        with db_manager.get_session() as session:
            legacy_id = item_data.get("id")
            existing = None
            try:
                # Use JSONB operator for reliable lookup
                existing = session.query(Experiment).filter(text("metadata->>'id' = :legacy_id")).params(legacy_id=str(legacy_id)).first() if legacy_id else None
            except Exception:
                existing = None

            if existing is None:
                model_instance = Experiment()
            else:
                model_instance = existing

            # Map simple columns
            if "experiment_status" in item_data:
                model_instance.status = item_data.get("experiment_status")
            # Derive a name for visibility if available
            name_candidate = (
                (item_data.get("config") or {}).get("name")
                if isinstance(item_data.get("config"), dict) else None
            ) or item_data.get("index_id") or ""
            if name_candidate:
                model_instance.experiment_name = name_candidate[:255]

            # Merge metadata
            metadata = dict(model_instance.metadata_json or {})
            for key in [
                "id",
                "execution_id",
                "config",
                "index_id",
                "experiment_status",
                "index_status",
                "retrieval_status",
                "eval_status",
            ]:
                if key in item_data:
                    metadata[key] = item_data[key]
            model_instance.metadata_json = metadata

            session.add(model_instance)
            session.flush()
            return self._experiment_to_legacy_dict(model_instance)

    def _read_experiments(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        with db_manager.get_session() as session:
            results = session.query(Experiment).all()

            def matches_filters(obj: Experiment) -> bool:
                if not filters:
                    return True
                md = obj.metadata_json or {}
                for k, v in filters.items():
                    if k == "experiment_status" and getattr(obj, "status", None) == v:
                        continue
                    if k == "id" and (md.get("id") == v or str(getattr(obj, "experiment_id", "")) == str(v)):
                        continue
                    if md.get(k) == v:
                        continue
                    return False
                return True

            return [self._experiment_to_legacy_dict(row) for row in results if matches_filters(row)]

    def _update_experiment_by_legacy_id(self, legacy_id: Any, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with db_manager.get_session() as session:
            try:
                obj = session.query(Experiment).filter(text("metadata->>'id' = :legacy_id")).params(legacy_id=str(legacy_id)).first()
            except Exception:
                obj = None
            if not obj:
                return None

            if "experiment_status" in update_data:
                obj.status = update_data["experiment_status"]

            metadata = dict(obj.metadata_json or {})
            metadata.update(update_data)
            obj.metadata_json = metadata

            session.flush()
            return self._experiment_to_legacy_dict(obj)

    def _experiment_to_legacy_dict(self, obj: Experiment) -> Dict[str, Any]:
        md = obj.metadata_json or {}
        return {
            "id": md.get("id") or (str(obj.experiment_id) if hasattr(obj, "experiment_id") else None),
            "experiment_status": obj.status,
            "index_status": md.get("index_status", "not_started"),
            "retrieval_status": md.get("retrieval_status", "not_started"),
            "eval_status": md.get("eval_status", "not_started"),
            "execution_id": md.get("execution_id"),
            "index_id": md.get("index_id"),
            "config": md.get("config"),
        }
    
    def batch_create_items(self, items_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple items in a batch."""
        try:
            with db_manager.get_session() as session:
                model_instances = [self.model_class(**item_data) for item_data in items_data]
                session.add_all(model_instances)
                session.flush()
                
                return [self._model_to_dict(instance) for instance in model_instances]
        except Exception as e:
            self.logger.error(f"Failed to batch create items in {self.table_name}: {e}")
            raise
    
    def execute_raw_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute raw SQL query."""
        try:
            with db_manager.get_session() as session:
                result = session.execute(text(query), params or {})
                return [dict(row._mapping) for row in result]
        except Exception as e:
            self.logger.error(f"Failed to execute raw query on {self.table_name}: {e}")
            raise
