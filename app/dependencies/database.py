from config.config import get_config
from ..orchestrator import StepFunctionOrchestrator
from flotorch_core.storage.db.db_storage import DBStorage
from flotorch_core.storage.db.postgresdb import PostgresDB
from flotorch_core.storage.db.dynamodb import DynamoDB
import databases
from typing import Optional, Union
from flotorch_core.config.env_config_provider import EnvConfigProvider
from flotorch_core.config.config_provider import ConfigProvider
from flotorch_core.config.config import Config

env_config_provider = EnvConfigProvider()
core_config = Config(env_config_provider)

# Dependency functions
def get_execution_db() -> DBStorage:
    yield from get_db_dependency(core_config.get_execution_table_name)

def get_experiment_db() -> DBStorage:
    yield from get_db_dependency(core_config.get_experiment_table_name)

def get_question_metrics_db() -> DBStorage:
    yield from get_db_dependency(core_config.get_experiment_question_metrics_table)

def get_execution_model_invocations_db() -> DBStorage:
    yield from get_db_dependency(core_config.get_execution_model_invocations_table)

def get_step_function_orchestrator() -> StepFunctionOrchestrator:
    return StepFunctionOrchestrator()


class DBClientFactory():
    def create_table_client(self, db_type: str, table_name: str) -> DBStorage:
        cache_name = f"{db_type}_{table_name}" if table_name else db_name
        if db_type == "DYNAMODB":
            return DynamoDB(
                table_name=table_name,
                region_name=core_config.get_region()
            )
        elif db_type == "POSTGRESDB":
            return PostgresDB(
                dbname=core_config.get_postgres_db(),
                user=core_config.get_postgres_user(),
                password=core_config.get_postgres_password(),
                table_name=table_name,
                host=core_config.get_postgres_host(),
                port=core_config.get_postgres_port()
            )
            
def get_db_dependency(table_name_func):
    """
    Generic generator dependency to create and clean up a DB client per request.
    """
    db_client: Optional[DBStorage] = None
    factory = DBClientFactory()
    db_type = core_config.get_db_type()
    table_name = table_name_func()

    if not table_name:
        raise RuntimeError(f"Configuration error: Missing table name for {table_name_func.__name__}")
    try:
        db_client = factory.create_table_client(db_type, table_name)
        if db_client is None:
             raise RuntimeError(f"Failed to create DB client instance for table {table_name}")
        yield db_client 

    except Exception as e:
        print(e)
        raise
    finally:
        if isinstance(db_client, PostgresDB):
            try:
                db_client.close()
            except Exception as e:
                logger.error(f"Error closing PostgresDB connection for {getattr(db_client, 'table', 'unknown')}: {e}", exc_info=True)
        elif isinstance(db_client, DynamoDB):
             pass