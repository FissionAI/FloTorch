import json
import math
import os
from fargate.base_task_processor import BaseFargateTaskProcessor
from decimal import Decimal
from .pricing import compute_actual_price_breakdown, calculate_experiment_duration
from flotorch_core.config.config import Config
from flotorch_core.config.env_config_provider import EnvConfigProvider
from flotorch_core.storage.db.postgresdb import PostgresDB
from flotorch_core.storage.db.dynamodb import DynamoDB
from flotorch_core.logger.global_logger import get_logger


MILLION = 1_000_000
THOUSAND = 1_000
SECONDS_IN_MINUTE = 60
MINUTES_IN_HOUR = 60
HOURS_IN_DAY = 24
DAYS_IN_MONTH = 30

logger = get_logger()
env_config_provider = EnvConfigProvider()
config = Config(env_config_provider)
db_type = config.get_db_type()

def fetch_data_from_db(table_name, key, value, index_name=None):
    """
    Fetch items with the specified key and value from DynamoDB or postgres based on db type.
    """
    try:
        if db_type == "DYNAMODB":
            db_client = DynamoDB(table_name=table_name, region_name=config.get_region())
            if index_name:
                items = db_client.read(keys={index_name: value})
            else:
                items = db_client.read(keys={key: value})

        elif db_type == "POSTGRESDB":
            db_client = PostgresDB(dbname=config.get_postgres_db(), user=config.get_postgres_user(), password=config.get_postgres_password(), table_name=table_name, host=config.get_postgres_host(), port=config.get_postgres_port())
            items = db_client.read(key={key: value})
        return items            
    except Exception as e:
        logger.error(f"Error fetching data from DB: {e}")
        raise


def validate_event(event):
    """
    Validate the input event to ensure required fields are present.
    """
    required_fields = ["experiment_id"]
    for field in required_fields:
        if field not in event:
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(event["experiment_id"], str):
        raise ValueError("'experiment_id' must be a string")


class RetrieverProcessor(BaseFargateTaskProcessor):
    """
    Processor for retriever tasks in Fargate.
    """

    def process(self):
        logger.info("Starting retriever process.")
        try:
            logger.info(f"Experiment Configuration received: {self.input_data}")

            # Validate input event
            validate_event(self.input_data)

            experiment_id = self.input_data["experiment_id"]
            experiment_table = config.get_experiment_table_name()
            experiment_question_metrics_table = config.get_experiment_question_metrics_table()
            experiment_question_metrics_index = os.getenv("experiment_question_metrics_index")

            if not experiment_table:
                raise EnvironmentError("Environment variable 'experiment_table' is not set")
            
            if not experiment_question_metrics_table:
                raise EnvironmentError("Environment variable 'experiment_question_metrics_table' is not set")
            
            # Initialize variables
            total_query_embed_tokens = 0
            total_answer_input_tokens = 0
            total_answer_output_tokens = 0

            experiment_items = fetch_data_from_db(experiment_table, 'id', experiment_id)
            experiment_question_metrics_items = fetch_data_from_db(experiment_question_metrics_table, 'experiment_id', experiment_id, experiment_question_metrics_index)
            total_duration = 0
            indexing_time = 0
            retrieval_time = 0
            eval_time = 0
            total_index_embed_tokens = 0

            if experiment_items:
                experiment = experiment_items[0]
                indexing_time, retrieval_time, eval_time = calculate_experiment_duration(experiment)
                indexing_time_in_min = math.ceil(indexing_time / SECONDS_IN_MINUTE)
                retrieval_time_in_min = math.ceil(retrieval_time / SECONDS_IN_MINUTE)
                eval_time_in_min = math.ceil(eval_time / SECONDS_IN_MINUTE)
                total_duration = indexing_time + retrieval_time + eval_time
                total_duration_in_min = indexing_time_in_min + retrieval_time_in_min + eval_time_in_min
                logger.info(f"Experiment {experiment_id} Total Time (in minutes): {total_duration_in_min} Indexing Time: {indexing_time_in_min}, Retrieval: {retrieval_time_in_min}, Evaluation: {eval_time_in_min}")

                total_index_embed_tokens = experiment.get("index_embed_tokens", 0)
                total_query_embed_tokens = experiment.get("retrieval_query_embed_tokens", 0)
                total_answer_input_tokens = experiment.get("retrieval_input_tokens", 1)
                total_answer_output_tokens = experiment.get("retrieval_output_tokens", 1)

            overall_metadata, indexing_metadata, retriever_metadata, inferencer_metadata, eval_metadata = compute_actual_price_breakdown(
                experiment,
                input_tokens=total_answer_input_tokens,
                output_tokens=total_answer_output_tokens,
                index_embed_tokens=total_index_embed_tokens,
                query_embed_tokens=total_query_embed_tokens,
                total_time=total_duration,
                indexing_time=indexing_time,
                retrieval_time=retrieval_time,
                eval_time=eval_time,
                experiment_question_metrics_items=experiment_question_metrics_items
            )

            total_cost = overall_metadata['total_cost']
            indexing_cost = indexing_metadata['total_cost']
            retriever_cost = retriever_metadata['total_cost']
            inferencer_cost = inferencer_metadata['total_cost']
            eval_cost = eval_metadata['total_cost']
            logger.info(f"Experiment {experiment_id} Actual Cost (in $): {total_cost}, Indexing: {indexing_cost}, Retrieval: {retriever_cost}, Inferencing: {inferencer_cost}, Evaluation : {eval_cost}")

            # Update DynamoDB with the new cost
            if total_cost is None:
                logger.error(f"Experiment {experiment_id} Actual Cost is None")
                total_cost = 0

            try:
                key={"id": experiment_id}
                data = {
                        "cost": str(total_cost),
                        "indexing_time": str(indexing_time),
                        "retrieval_time": str(retrieval_time),
                        "eval_time": str(eval_time),
                        "total_time": str(total_duration),
                        "indexing_cost": str(indexing_cost),
                        "retrieval_cost": str(retriever_cost),
                        "inferencing_cost": str(inferencer_cost),
                        "eval_cost": str(eval_cost),
                        "indexing_metadata": convert_floats_to_decimal(indexing_metadata),
                        "retriever_metadata": convert_floats_to_decimal(retriever_metadata),
                        "inferencer_metadata": convert_floats_to_decimal(inferencer_metadata),
                        "eval_metadata": convert_floats_to_decimal(eval_metadata),
                        "overall_metadata": convert_floats_to_decimal(overall_metadata)
                    }
                if db_type == "DYNAMODB":
                    db_client = DynamoDB(table_name=experiment_table, region_name=config.get_region())
                elif db_type == "POSTGRESDB":
                    db_client = PostgresDB(dbname=config.get_postgres_db(), user=config.get_postgres_user(), password=config.get_postgres_password(), table_name=experiment_table, host=config.get_postgres_host(), port=config.get_postgres_port())

                db_client.update(key, data)
                    
            except Exception as e:
                logger.error(f"Error updating DB: {e}")
                raise

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "total_cost": total_cost,
                        "dynamodb_update_count": len(experiment_items),
                    }
                ),
            }

        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
            return {"statusCode": 400, "body": json.dumps({"error": str(ve)})}
        except EnvironmentError as ee:
            logger.error(f"Environment error: {ee}")
            return {"statusCode": 500, "body": json.dumps({"error": str(ee)})}
        except Exception as e:
            logger.error(f"Unhandled error: {e}")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Internal server error"}),
            }

def convert_floats_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))  # Convert float to string first to prevent precision loss
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(i) for i in obj]
    else:
        return obj