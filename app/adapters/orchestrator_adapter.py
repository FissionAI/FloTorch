"""
Orchestrator adapter with feature flag to switch between Step Functions and direct service calls.
"""
import os
import json
import boto3
import logging
from typing import Dict, Any
from fastapi import HTTPException
from config.config import get_config
from app.adapters.retriever_adapter import RetrieverAdapter
from app.adapters.indexer_adapter import IndexerAdapter
from app.adapters.eval_adapter import EvalAdapter

logger = logging.getLogger(__name__)

class OrchestratorAdapter:
    """
    Adapter that can use either Step Functions or direct service calls for orchestration.
    Controlled by USE_DIRECT_ORCHESTRATION environment variable.
    """
    
    def __init__(self):
        self.config = get_config()
        self.use_direct = os.getenv("USE_DIRECT_ORCHESTRATION", "false").lower() == "true"
        
        if self.use_direct:
            logger.info("Using direct service orchestration")
            self._init_direct_orchestration()
        else:
            logger.info("Using Step Functions orchestration")
            self._init_step_functions()
    
    def _init_direct_orchestration(self):
        """Initialize direct service orchestration."""
        # Initialize service adapters
        self.retriever = RetrieverAdapter({}, {})
        self.indexer = IndexerAdapter({}, {})
        self.eval = EvalAdapter({}, {})
    
    def _init_step_functions(self):
        """Initialize Step Functions orchestration."""
        try:
            self.step_function_client = boto3.client(
                "stepfunctions", 
                region_name=self.config.aws_region
            )
        except Exception as e:
            logger.error(f"Failed to initialize Step Function client: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to initialize AWS Step Function client"
            )
    
    def run_experiment_orchestration(self, execution_id: str) -> Dict[str, Any]:
        """
        Execute experiment orchestration using either Step Functions or direct calls.
        
        Args:
            execution_id (str): The execution ID
            
        Returns:
            Dict[str, Any]: Response from orchestration
        """
        if self.use_direct:
            return self._run_direct_orchestration(execution_id)
        else:
            return self._run_step_functions_orchestration(execution_id)
    
    def _run_direct_orchestration(self, execution_id: str) -> Dict[str, Any]:
        """Execute orchestration using direct service calls."""
        try:
            logger.info(f"Starting direct orchestration for execution: {execution_id}")
            
            # Load execution and experiment configs from database
            # This would need to be implemented based on your data access patterns
            config = self.config
            experimental_config = self._load_experimental_config(execution_id)
            
            # Execute pipeline steps in sequence
            results = {}
            
            # Step 1: Indexing (if needed)
            if experimental_config.get('needs_indexing', False):
                logger.info("Executing indexing step")
                self.indexer.chunk_embed_store(config, experimental_config)
                results['indexing'] = 'completed'
            
            # Step 2: Retrieval
            logger.info("Executing retrieval step")
            self.retriever.retrieve(config, experimental_config)
            results['retrieval'] = 'completed'
            
            # Step 3: Evaluation (if needed)
            if experimental_config.get('needs_evaluation', False):
                logger.info("Executing evaluation step")
                self.eval.evaluate(config, experimental_config)
                results['evaluation'] = 'completed'
            
            logger.info(f"Direct orchestration completed for execution: {execution_id}")
            return {
                'executionArn': f'direct-{execution_id}',
                'status': 'SUCCEEDED',
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Direct orchestration failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Direct orchestration failed: {str(e)}"
            )
    
    def _run_step_functions_orchestration(self, execution_id: str) -> Dict[str, Any]:
        """Execute orchestration using Step Functions."""
        try:
            payload = {"execution_id": execution_id}
            response = self.step_function_client.start_execution(
                stateMachineArn=self.config.step_function_arn,
                input=json.dumps(payload)
            )
            
            logger.info(f"Started Step Function with Execution ARN: {response['executionArn']}")
            return response
            
        except Exception as e:
            error_message = f"Failed to execute Step Functions orchestration: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise HTTPException(status_code=500, detail=error_message)
    
    def _load_experimental_config(self, execution_id: str) -> Dict[str, Any]:
        """Load experimental configuration for execution."""
        # This is a placeholder - you would implement actual database loading here
        # For now, return a basic config
        return {
            'execution_id': execution_id,
            'needs_indexing': True,
            'needs_evaluation': True
        }
