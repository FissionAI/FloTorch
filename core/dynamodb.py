import boto3
import logging
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError
from decimal import Decimal
import json
import time
from datetime import datetime, timezone

class DynamoDBOperations:
    """Class to handle DynamoDB operations."""

    def __init__(self, table_name: str, region: str = 'us-east-1'):
        """
        Initialize DynamoDB operations.

        Args:
            table_name (str): DynamoDB table name
            region (str): AWS region
        """
        self.table_name = table_name
        self.region = region
        self.logger = logging.getLogger(__name__)
        
        # Initialize DynamoDB resources
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
        
        # Initialize DynamoDB client for batch operations
        self.dynamodb_client = boto3.client('dynamodb', region_name=region)

    def _handle_decimal_type(self, obj: Any) -> Any:
        """
        Handle Decimal type for DynamoDB.

        Args:
            obj: Input object to process

        Returns:
            Processed object with Decimal types handled
        """
        if isinstance(obj, list):
            return [self._handle_decimal_type(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: self._handle_decimal_type(v) for k, v in obj.items()}
        elif isinstance(obj, float):
            return Decimal(str(obj))
        return obj

    def _serialize_datetime(self, obj: Any) -> Any:
        """
        Recursively serialize datetime objects into string format.
        """
        if isinstance(obj, list):
            return [self._serialize_datetime(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: self._serialize_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO 8601 string
        return obj
    
    def scan_all(self, filter_expression: Optional[str] = None, expression_values: Optional[Dict[str, Any]] = None, expression_attribute_names: Optional[Dict[str, str]] = None) -> Dict:
        """
        Scan items from DynamoDB, optionally applying filter expressions.

        Args:
            filter_expression (Optional[str]): Filter expression for the scan.
            expression_values (Optional[Dict[str, Any]]): Attribute values for the filter.
            expression_attribute_names (Optional[Dict[str, str]]): Attribute names mapping for reserved keywords.

        Returns:
            Dict: Scan results.
        """
        result = []
        try:
            params = {}
            if filter_expression:
                params["FilterExpression"] = filter_expression
            if expression_values:
                params["ExpressionAttributeValues"] = self._handle_decimal_type(expression_values)
            if expression_attribute_names:
                params["ExpressionAttributeNames"] = expression_attribute_names

            while True:
                response = self.table.scan(**params)
                result.extend(response.get('Items', []))
                last_evaluated_key = response.get('LastEvaluatedKey')

                if not last_evaluated_key:
                    break

            return response
        except Exception as e:
            self.logger.error(f"Error scanning items: {str(e)}")
            raise


    def scan(self, filter_expression: Optional[str] = None, expression_values: Optional[Dict[str, Any]] = None, expression_attribute_names: Optional[Dict[str, str]] = None) -> Dict:
        """
        Scan items from DynamoDB, optionally applying filter expressions.

        Args:
            filter_expression (Optional[str]): Filter expression for the scan.
            expression_values (Optional[Dict[str, Any]]): Attribute values for the filter.
            expression_attribute_names (Optional[Dict[str, str]]): Attribute names mapping for reserved keywords.

        Returns:
            Dict: Scan results.
        """
        try:
            params = {}
            if filter_expression:
                params["FilterExpression"] = filter_expression
            if expression_values:
                params["ExpressionAttributeValues"] = self._handle_decimal_type(expression_values)
            if expression_attribute_names:
                params["ExpressionAttributeNames"] = expression_attribute_names

            response = self.table.scan(**params)
            return response

        except Exception as e:
            self.logger.error(f"Error scanning items: {str(e)}")
            raise

    
    def _serialize_data(self, obj: Any) -> Any:
        """
        Recursively convert float to Decimal and serialize datetime to string.
        """
        if isinstance(obj, list):
            return [self._serialize_data(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: self._serialize_data(v) for k, v in obj.items()}
        elif isinstance(obj, float):
            return Decimal(str(obj))  # Convert float to Decimal
        elif isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO 8601 string
        return obj
    
    def get_item(self, key: Dict[str, Any]) -> Optional[Dict]:
        """
        Retrieve an item from DynamoDB.

        Args:
            key (Dict[str, Any]): Primary key of the item

        Returns:
            Optional[Dict]: Item if found, None otherwise
        """
        try:
            response = self.table.get_item(Key=key)
            item = response.get('Item')
            
            if item:
                self.logger.info(f"Successfully retrieved item with key: {key}")
                return item
            
            self.logger.info(f"No item found with key: {key}")
            return None

        except ClientError as e:
            self.logger.error(f"Error retrieving item with key {key}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise

    def put_item(self, item: Dict[str, Any], condition_expression: str = None, add_metadata: bool = True) -> Dict:
        """
        Put an item into DynamoDB.

        Args:
            item (Dict[str, Any]): Item to put.
            condition_expression (str, optional): Condition expression for the put operation.
            add_metadata (bool, optional): Whether to add timestamp and last_updated metadata. Default is True.

        Returns:
            Dict: Response from DynamoDB.
        """
        try:
            # Add metadata if required
            if add_metadata:
                item["timestamp"] = datetime.now(timezone.utc).isoformat()
                item["last_updated"] = datetime.now(timezone.utc).isoformat()

            # Serialize data to handle unsupported types like datetime
            serialized_item = self._serialize_data(item)

            # Prepare put_item parameters
            params = {
                "Item": serialized_item
            }

            if condition_expression:
                params["ConditionExpression"] = condition_expression

            # Put the item into DynamoDB
            response = self.table.put_item(**params)

            # Log success
            self.logger.info(f"Successfully put item: {item.get('id', 'No ID')}")
            return response

        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                self.logger.warning("Condition check failed for put_item operation")
            else:
                self.logger.error(f"Error putting item: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise



    def update_item(self, 
                    key: Dict[str, Any], 
                    update_expression: str, 
                    expression_values: Dict[str, Any],
                    condition_expression: str = None) -> Dict:
        """
        Update an item in DynamoDB.

        Args:
            key (Dict[str, Any]): Primary key of the item
            update_expression (str): Update expression
            expression_values (Dict[str, Any]): Expression attribute values
            condition_expression (str, optional): Condition expression

        Returns:
            Dict: Response from DynamoDB
        """
        try:
            # Add last_updated to expression values
            #expression_values[':updated'] = datetime.utcnow().isoformat()
            #update_expression += ', last_updated = :updated'
            
            # Handle decimal types in expression values
            processed_values = self._handle_decimal_type(expression_values)
            
            # Prepare update parameters
            params = {
                'Key': key,
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': processed_values,
                'ReturnValues': 'UPDATED_NEW'
            }
            
            if condition_expression:
                params['ConditionExpression'] = condition_expression
            
            response = self.table.update_item(**params)
            
            self.logger.info(f"Successfully updated item with key: {key}")
            return response

        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                self.logger.warning("Condition check failed for update operation")
            else:
                self.logger.error(f"Error updating item: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise

    def query(self, 
              key_condition_expression: str,
              expression_values: Dict[str, Any],
              index_name: str = None, projection: str = None) -> Dict:
        """
        Query items from DynamoDB.

        Args:
            key_condition_expression (str): Key condition expression
            expression_values (Dict[str, Any]): Expression attribute values
            index_name (str, optional): Name of the index to query

        Returns:
            Dict: Query results
        """
        try:
            # Handle decimal types in expression values
            processed_values = self._handle_decimal_type(expression_values)
            
            # Prepare query parameters
            params = {
                'KeyConditionExpression': key_condition_expression,
                'ExpressionAttributeValues': processed_values
            }
            
            if index_name:
                params['IndexName'] = index_name
            
            if projection:
                params['ProjectionExpression'] = projection
            
            response = self.table.query(**params)
            
            self.logger.info(f"Successfully queried {len(response['Items'])} items")
            return response

        except ClientError as e:
            self.logger.error(f"Error querying items: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise

    def batch_write(self, items: List[Dict[str, Any]], max_retries: int = 3) -> None:
        """
        Batch write items to DynamoDB with automatic retry and backoff.
        DynamoDB has a limit of 25 items per batch write operation.

        Args:
            items (List[Dict[str, Any]]): List of items to write (max 25 items)
            max_retries (int): Maximum number of retries for failed items
        """
        try:
            if len(items) > 25:
                raise ValueError("DynamoDB batch_write_item operation can only process up to 25 items at a time")
                
            unprocessed_items = items
            retry_count = 0
            
            while unprocessed_items and retry_count < max_retries:
                # Prepare batch write request
                request_items = {
                    self.table_name: [
                        {
                            'PutRequest': {
                                'Item': self._handle_decimal_type(item)
                            }
                        }
                        for item in unprocessed_items
                    ]
                }
                
                response = self.dynamodb_client.batch_write_item(
                    RequestItems=request_items
                )
                
                # Handle unprocessed items
                unprocessed_items = [
                    item['PutRequest']['Item']
                    for item in response.get('UnprocessedItems', {}).get(self.table_name, [])
                ]
                
                if unprocessed_items:
                    retry_count += 1
                    if retry_count < max_retries:
                        # Exponential backoff
                        time.sleep(2 ** retry_count)
            
            if unprocessed_items:
                self.logger.warning(f"{len(unprocessed_items)} items remained unprocessed after {max_retries} retries")
            else:
                self.logger.info(f"Successfully batch wrote {len(items)} items")

        except ClientError as e:
            self.logger.error(f"Error in batch write operation: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise

    def delete_item(self, key: Dict[str, Any], condition_expression: str = None) -> Dict:
        """
        Delete an item from DynamoDB.

        Args:
            key (Dict[str, Any]): Primary key of the item
            condition_expression (str, optional): Condition expression

        Returns:
            Dict: Response from DynamoDB
        """
        try:
            params = {'Key': key}
            
            if condition_expression:
                params['ConditionExpression'] = condition_expression
            
            response = self.table.delete_item(**params)
            
            self.logger.info(f"Successfully deleted item with key: {key}")
            return response

        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                self.logger.warning("Condition check failed for delete operation")
            else:
                self.logger.error(f"Error deleting item: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise
