import csv
import io
import logging
from datetime import datetime, timezone
from typing import Optional

import boto3
import pandas as pd
from botocore.exceptions import ClientError


def read_csv_from_s3(object_key: str, bucket_name: str, as_dataframe: bool = True) -> Optional[object]:
    """
    Read CSV data from S3 and convert it to a list of dictionaries or a pandas DataFrame.
    Args:
        object_key (str): The key (path) of the S3 object.
        bucket_name (str): The name of the S3 bucket.
        as_dataframe (bool): If True, return a pandas DataFrame, otherwise return a list of dictionaries.
    Returns:
        Optional[object]: List of dictionaries or pandas DataFrame containing the CSV data if successful, None otherwise.
    Raises:
        ClientError: If there's an error accessing S3.
        csv.Error: If the content cannot be parsed as CSV.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Initialize the S3 client
    s3_client = boto3.client('s3')

    try:
        logger.info(f"Reading file from S3: Bucket={bucket_name}, Key={object_key}")

        # Get the object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)

        # Read the data
        file_content = response['Body'].read().decode('utf-8')

        if as_dataframe:
            # Parse content into a pandas DataFrame
            csv_data = pd.read_csv(io.StringIO(file_content), float_precision="round_trip")
        else:
            # Parse content into a list of dictionaries
            csv_reader = csv.DictReader(file_content.splitlines())
            csv_data = [row for row in csv_reader]

        return csv_data

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', 'Unknown error')
        logger.error(f"Failed to read from S3: {error_code} - {error_message}", exc_info=True)
        raise

    except csv.Error as e:
        logger.error(f"Failed to parse CSV content from {bucket_name}/{object_key}", exc_info=True)
        raise

    except Exception as e:
        logger.error(f"Unexpected error reading from S3: {str(e)}", exc_info=True)
        raise

def parse_datetime(datetime_str):
    if not datetime_str:
        return None
    try:
        dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S%z')

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt