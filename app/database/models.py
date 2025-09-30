"""
PostgreSQL database models for FloTorch application.
"""
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Experiment(Base):
    """Experiment table model."""
    __tablename__ = "experiments"
    
    experiment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="created")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Configuration fields
    aws_region = Column(String(50))
    s3_bucket = Column(String(255))
    opensearch_host = Column(String(255))
    opensearch_serverless = Column(Boolean, default=False)
    
    # Experiment settings
    chunking_algorithm = Column(String(100))
    embedding_model = Column(String(100))
    inference_model = Column(String(100))
    indexing_algorithm = Column(String(100))
    
    # Metadata (SQLAlchemy reserves attribute name 'metadata')
    metadata_json = Column('metadata', JSONB)
    
    # Indexes
    __table_args__ = (
        Index('idx_experiments_status', 'status'),
        Index('idx_experiments_created_at', 'created_at'),
    )

class Execution(Base):
    """Execution table model."""
    __tablename__ = "executions"
    
    execution_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), nullable=False)
    execution_name = Column(String(255))
    status = Column(String(50), nullable=False, default="pending")
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Execution details
    step_function_arn = Column(String(255))
    step_function_execution_arn = Column(String(255))
    
    # Results
    total_questions = Column(Integer, default=0)
    completed_questions = Column(Integer, default=0)
    failed_questions = Column(Integer, default=0)
    
    # Metadata (SQLAlchemy reserves attribute name 'metadata')
    metadata_json = Column('metadata', JSONB)
    
    # Indexes
    __table_args__ = (
        Index('idx_executions_experiment_id', 'experiment_id'),
        Index('idx_executions_status', 'status'),
        Index('idx_executions_created_at', 'created_at'),
    )

class QuestionMetrics(Base):
    """Question metrics table model."""
    __tablename__ = "question_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), nullable=False)
    execution_id = Column(UUID(as_uuid=True), nullable=False)
    question_id = Column(String(255), nullable=False)
    
    # Question and answer data
    question = Column(Text, nullable=False)
    ground_truth_answer = Column(Text)
    generated_answer = Column(Text)
    
    # Metrics
    answer_accuracy = Column(Float)
    answer_relevance = Column(Float)
    answer_coherence = Column(Float)
    answer_fluency = Column(Float)
    overall_score = Column(Float)
    
    # Timing
    retrieval_time = Column(Float)  # seconds
    generation_time = Column(Float)  # seconds
    total_time = Column(Float)  # seconds
    
    # Cost tracking
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    
    # Status
    status = Column(String(50), default="pending")
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Metadata (SQLAlchemy reserves attribute name 'metadata')
    metadata_json = Column('metadata', JSONB)
    
    # Indexes
    __table_args__ = (
        Index('idx_question_metrics_experiment_id', 'experiment_id'),
        Index('idx_question_metrics_execution_id', 'execution_id'),
        Index('idx_question_metrics_question_id', 'question_id'),
        Index('idx_question_metrics_status', 'status'),
    )

class ModelInvocations(Base):
    """Model invocations tracking table."""
    __tablename__ = "model_invocations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), nullable=False)
    question_id = Column(String(255), nullable=False)
    
    # Model details
    model_name = Column(String(255), nullable=False)
    model_type = Column(String(50), nullable=False)  # embedding, inference, etc.
    
    # Request/Response data
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    
    # Performance metrics
    latency_ms = Column(Float)
    cost = Column(Float, default=0.0)
    
    # Status
    status = Column(String(50), default="success")
    error_message = Column(Text)
    
    # Timestamps
    invoked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_model_invocations_execution_id', 'execution_id'),
        Index('idx_model_invocations_question_id', 'question_id'),
        Index('idx_model_invocations_model_name', 'model_name'),
        Index('idx_model_invocations_invoked_at', 'invoked_at'),
    )
