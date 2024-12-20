Pricing Engine
==============

The Pricing Engine estimates and calculates costs for running experiments with LLM models, covering key infrastructure and service components.

Features
--------

### OpenSearch

-   Calculates based on the RPM (Requests Per Minute) of Bedrock models for indexing, retrieval, and evaluation

### ECS (Fargate)

-   Calculates ECS costs for indexing, retrieval, and evaluation tasks
-   Uses 8 vCPU, 16 GB memory configuration

### Bedrock Token Costs

-   **Embeddings**: Calculates costs based on the number of tokens processed
-   **Inference Input and Output**: Computes costs using token counts for both input and output during inference

### Additional Services

-   Includes percentage markup for costs from supporting services:
    -   S3
    -   DynamoDB
    -   ECR
    -   VPC

Workflow
--------

### Directional Pricing

Provides approximate pricing before experiments based on reasonable assumptions, including:

Token Counts
------------

-   Estimates token counts for:
    -   Embeddings
    -   Inference inputs and outputs
-   Based on:
    -   Knowledge base
    -   Ground truth
    -   Chunking strategy
        -   Number of tokens per chunk
        -   Percentage overlap
    -   Retrieval strategy
        -   Number of prompts
        -   KNN value

Runtime Estimates
-----------------

-   Assumes average time per operation for:
    -   Indexing
    -   Retrieval
    -   Evaluation tasks
-   Takes into account:
    -   OpenSearch RPM limits
    -   Bedrock RPM limits

### Estimation Cost

Post-experiment, the Pricing Engine replaces initial assumptions with actual metrics:

-   Runtime per operation for:
    -   Indexing
    -   Retrieval
    -   Evaluation
    -   Overall experiment duration (from DynamoDB)
-   Exact token usage captured during:
    -   Indexing processes
    -   Retrieval processes