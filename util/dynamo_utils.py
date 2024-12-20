from typing import Dict, Any

import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def deserialize_dynamodb_json(dynamodb_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deserialize DynamoDB JSON to regular Python dictionary.
    
    Args:
        dynamodb_json (Dict[str, Any]): DynamoDB JSON formatted dictionary
        
    Returns:
        Dict[str, Any]: Regular Python dictionary
    """
    # Handle None/Null response from DynamoDB
    if dynamodb_json is None:
        return None
        
    try:
        def _deserialize_value(value: Dict[str, Any]) -> Any:
            if not isinstance(value, dict):
                return value
                
            if 'N' in value:
                return float(value['N'])
            elif 'S' in value:
                return value['S']
            elif 'BOOL' in value:
                return value['BOOL']
            elif 'NULL' in value:
                return None
            elif 'L' in value:
                return [_deserialize_value(item) for item in value['L']]
            elif 'M' in value:
                return {k: _deserialize_value(v) for k, v in value['M'].items()}
            elif 'SS' in value:
                return set(value['SS'])
            elif 'NS' in value:
                return {float(n) for n in value['NS']}
            elif 'Nul' in value:
                return None
            else:
                return value

        return {k: _deserialize_value(v) for k, v in dynamodb_json.items()}

    except Exception as e:
        logger.error(f"Error deserializing DynamoDB JSON: {e}")
        raise