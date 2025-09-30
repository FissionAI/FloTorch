"""
Dual write adapter that writes to both DynamoDB and PostgreSQL during migration.
"""
import os
import logging
from typing import Dict, Any, Optional, List
from app.adapters.postgres_adapter import PostgresAdapter
from flotorch_core.storage.db.db_storage import DBStorage
import boto3

logger = logging.getLogger(__name__)

class DualWriteAdapter:
    """
    Adapter that writes to both DynamoDB and PostgreSQL for gradual migration.
    Reads can be configured to use either database as primary.
    """
    
    def __init__(self, table_name: str, aws_region: str = "us-east-1", **kwargs):
        self.table_name = table_name
        self.aws_region = aws_region
        
        # Configuration flags
        self.dual_write_enabled = os.getenv("ENABLE_DUAL_WRITES", "false").lower() == "true"
        self.read_from_postgres = os.getenv("READ_FROM_POSTGRES", "false").lower() == "true"
        
        # Initialize adapters
        self.postgres_adapter = PostgresAdapter(table_name=table_name, **kwargs)
        self.dynamodb_adapter = None
        
        if self.dual_write_enabled:
            self._init_dynamodb_adapter()
        
        logger.info(f"DualWriteAdapter initialized for {table_name}: "
                   f"dual_write={self.dual_write_enabled}, "
                   f"read_from_postgres={self.read_from_postgres}")
    
    def _init_dynamodb_adapter(self):
        """Initialize DynamoDB adapter for dual writes."""
        try:
            # Map table names to DynamoDB table names
            table_mapping = {
                "experiments": os.getenv("experiment_table", "flotorch_experiment"),
                "executions": os.getenv("execution_table", "flotorch_execution"),
                "question_metrics": os.getenv("experiment_question_metrics_table", "flotorch_question_metrics"),
                "model_invocations": os.getenv("execution_model_invocations_table", "flotorch_model_invocations")
            }

            dynamodb_table = table_mapping.get(self.table_name)
            if not dynamodb_table:
                logger.warning(f"No DynamoDB table mapping for {self.table_name}")
                return

            # Create a lightweight wrapper around boto3 client to mimic the previous API
            ddb_client = boto3.client("dynamodb", region_name=self.aws_region)

            class _TableWrapper:
                def __init__(self, client, table_name):
                    self._client = client
                    self._name = table_name

                def put_item(self, **kwargs):
                    return self._client.put_item(TableName=self._name, **kwargs)

                def get_item(self, **kwargs):
                    return self._client.get_item(TableName=self._name, **kwargs)

                def update_item(self, **kwargs):
                    return self._client.update_item(TableName=self._name, **kwargs)

                def delete_item(self, **kwargs):
                    return self._client.delete_item(TableName=self._name, **kwargs)

                def scan(self, **kwargs):
                    return self._client.scan(TableName=self._name, **kwargs)

            class _DynAdapter:
                def __init__(self, client, table_name):
                    self.table = _TableWrapper(client, table_name)

            self.dynamodb_adapter = _DynAdapter(ddb_client, dynamodb_table)
            logger.info(f"DynamoDB adapter initialized for {self.table_name} -> {dynamodb_table}")

        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB adapter: {e}")
            self.dynamodb_adapter = None
    
    def create_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create item in both databases if dual write is enabled."""
        results = {}
        primary_result = None
        
        try:
            # Write to PostgreSQL (always primary for writes)
            primary_result = self.postgres_adapter.create_item(item_data)
            results["postgresql"] = {"status": "success", "data": primary_result}
            
            # Write to DynamoDB if dual write is enabled
            if self.dual_write_enabled and self.dynamodb_adapter:
                try:
                    dynamodb_result = self._create_dynamodb_item(item_data)
                    results["dynamodb"] = {"status": "success", "data": dynamodb_result}
                except Exception as e:
                    logger.error(f"DynamoDB dual write failed: {e}")
                    results["dynamodb"] = {"status": "failed", "error": str(e)}
            
            return primary_result
            
        except Exception as e:
            logger.error(f"Primary write (PostgreSQL) failed: {e}")
            results["postgresql"] = {"status": "failed", "error": str(e)}
            raise
    
    def get_item(self, key: str, value: Any) -> Optional[Dict[str, Any]]:
        """Get item from configured primary database."""
        if self.read_from_postgres:
            # Read from PostgreSQL
            try:
                result = self.postgres_adapter.get_item(key, value)
                if result:
                    return result
            except Exception as e:
                logger.error(f"PostgreSQL read failed: {e}")
                # Fallback to DynamoDB
                if self.dynamodb_adapter:
                    return self._get_dynamodb_item(key, value)
        else:
            # Read from DynamoDB (legacy behavior)
            if self.dynamodb_adapter:
                result = self._get_dynamodb_item(key, value)
                if result:
                    return result
            
            # Fallback to PostgreSQL
            try:
                return self.postgres_adapter.get_item(key, value)
            except Exception as e:
                logger.error(f"PostgreSQL fallback read failed: {e}")
        
        return None
    
    def update_item(self, key: str, value: Any, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update item in both databases if dual write is enabled."""
        results = {}
        primary_result = None
        
        try:
            # Update PostgreSQL (always primary for writes)
            primary_result = self.postgres_adapter.update_item(key, value, update_data)
            results["postgresql"] = {"status": "success", "data": primary_result}
            
            # Update DynamoDB if dual write is enabled
            if self.dual_write_enabled and self.dynamodb_adapter:
                try:
                    dynamodb_result = self._update_dynamodb_item(key, value, update_data)
                    results["dynamodb"] = {"status": "success", "data": dynamodb_result}
                except Exception as e:
                    logger.error(f"DynamoDB dual write update failed: {e}")
                    results["dynamodb"] = {"status": "failed", "error": str(e)}
            
            return primary_result
            
        except Exception as e:
            logger.error(f"Primary update (PostgreSQL) failed: {e}")
            results["postgresql"] = {"status": "failed", "error": str(e)}
            raise
    
    def delete_item(self, key: str, value: Any) -> bool:
        """Delete item from both databases if dual write is enabled."""
        results = {}
        primary_result = False
        
        try:
            # Delete from PostgreSQL (always primary for writes)
            primary_result = self.postgres_adapter.delete_item(key, value)
            results["postgresql"] = {"status": "success", "deleted": primary_result}
            
            # Delete from DynamoDB if dual write is enabled
            if self.dual_write_enabled and self.dynamodb_adapter:
                try:
                    dynamodb_result = self._delete_dynamodb_item(key, value)
                    results["dynamodb"] = {"status": "success", "deleted": dynamodb_result}
                except Exception as e:
                    logger.error(f"DynamoDB dual write delete failed: {e}")
                    results["dynamodb"] = {"status": "failed", "error": str(e)}
            
            return primary_result
            
        except Exception as e:
            logger.error(f"Primary delete (PostgreSQL) failed: {e}")
            results["postgresql"] = {"status": "failed", "error": str(e)}
            raise
    
    def query_items(self, filters: Optional[Dict[str, Any]] = None, 
                   limit: Optional[int] = None, 
                   offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Query items from configured primary database."""
        if self.read_from_postgres:
            # Query PostgreSQL
            try:
                return self.postgres_adapter.query_items(filters, limit, offset)
            except Exception as e:
                logger.error(f"PostgreSQL query failed: {e}")
                # Fallback to DynamoDB
                if self.dynamodb_adapter:
                    return self._query_dynamodb_items(filters, limit, offset)
        else:
            # Query DynamoDB (legacy behavior)
            if self.dynamodb_adapter:
                result = self._query_dynamodb_items(filters, limit, offset)
                if result:
                    return result
            
            # Fallback to PostgreSQL
            try:
                return self.postgres_adapter.query_items(filters, limit, offset)
            except Exception as e:
                logger.error(f"PostgreSQL fallback query failed: {e}")
        
        return []
    
    def _create_dynamodb_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create item in DynamoDB."""
        # Convert PostgreSQL format to DynamoDB format
        dynamodb_item = self._convert_to_dynamodb_format(item_data)
        
        response = self.dynamodb_adapter.table.put_item(Item=dynamodb_item)
        return {"status": "created", "item": item_data}
    
    def _get_dynamodb_item(self, key: str, value: Any) -> Optional[Dict[str, Any]]:
        """Get item from DynamoDB."""
        try:
            response = self.dynamodb_adapter.table.get_item(
                Key={key: {"S": str(value)}}
            )
            
            if "Item" in response:
                return self._convert_from_dynamodb_format(response["Item"])
            return None
        except Exception as e:
            logger.error(f"DynamoDB get_item failed: {e}")
            return None
    
    def _update_dynamodb_item(self, key: str, value: Any, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update item in DynamoDB."""
        # Convert update data to DynamoDB format
        dynamodb_update = self._convert_to_dynamodb_format(update_data)
        
        # Build update expression
        update_expression = "SET " + ", ".join([f"{k} = :{k}" for k in update_data.keys()])
        expression_values = {f":{k}": dynamodb_update[k] for k in update_data.keys()}
        
        response = self.dynamodb_adapter.table.update_item(
            Key={key: {"S": str(value)}},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues="ALL_NEW"
        )
        
        return {"status": "updated", "data": update_data}
    
    def _delete_dynamodb_item(self, key: str, value: Any) -> bool:
        """Delete item from DynamoDB."""
        try:
            response = self.dynamodb_adapter.table.delete_item(
                Key={key: {"S": str(value)}}
            )
            return True
        except Exception as e:
            logger.error(f"DynamoDB delete_item failed: {e}")
            return False
    
    def _query_dynamodb_items(self, filters: Optional[Dict[str, Any]] = None, 
                             limit: Optional[int] = None, 
                             offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Query items from DynamoDB."""
        try:
            # Simple scan implementation - in practice, you'd want to use query with indexes
            scan_params = {}
            if limit:
                scan_params["Limit"] = limit
            
            response = self.dynamodb_adapter.table.scan(**scan_params)
            items = response.get("Items", [])
            
            return [self._convert_from_dynamodb_format(item) for item in items]
        except Exception as e:
            logger.error(f"DynamoDB query failed: {e}")
            return []
    
    def _convert_to_dynamodb_format(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert PostgreSQL item format to DynamoDB format."""
        dynamodb_item = {}
        
        for key, value in item_data.items():
            if value is None:
                continue
            elif isinstance(value, str):
                dynamodb_item[key] = {"S": value}
            elif isinstance(value, (int, float)):
                dynamodb_item[key] = {"N": str(value)}
            elif isinstance(value, bool):
                dynamodb_item[key] = {"BOOL": value}
            elif isinstance(value, dict):
                dynamodb_item[key] = {"M": self._convert_dict_to_dynamodb(value)}
            else:
                dynamodb_item[key] = {"S": str(value)}
        
        return dynamodb_item
    
    def _convert_from_dynamodb_format(self, dynamodb_item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert DynamoDB item format to PostgreSQL format."""
        item = {}
        
        for key, value in dynamodb_item.items():
            if "S" in value:
                item[key] = value["S"]
            elif "N" in value:
                try:
                    item[key] = float(value["N"]) if "." in value["N"] else int(value["N"])
                except:
                    item[key] = value["N"]
            elif "BOOL" in value:
                item[key] = value["BOOL"]
            elif "M" in value:
                item[key] = self._convert_dynamodb_map(value["M"])
            else:
                item[key] = value
        
        return item
    
    def _convert_dict_to_dynamodb(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert nested dictionary to DynamoDB format."""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = {"S": value}
            elif isinstance(value, (int, float)):
                result[key] = {"N": str(value)}
            elif isinstance(value, bool):
                result[key] = {"BOOL": value}
            elif isinstance(value, dict):
                result[key] = {"M": self._convert_dict_to_dynamodb(value)}
            else:
                result[key] = {"S": str(value)}
        return result
    
    def _convert_dynamodb_map(self, dynamodb_map: Dict[str, Any]) -> Dict[str, Any]:
        """Convert DynamoDB map to regular dictionary."""
        result = {}
        for key, value in dynamodb_map.items():
            if "S" in value:
                result[key] = value["S"]
            elif "N" in value:
                try:
                    result[key] = float(value["N"]) if "." in value["N"] else int(value["N"])
                except:
                    result[key] = value["N"]
            elif "BOOL" in value:
                result[key] = value["BOOL"]
            elif "M" in value:
                result[key] = self._convert_dynamodb_map(value["M"])
        return result
