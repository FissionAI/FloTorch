## Release v1.0.2 - 2024-12-31

### New Features
- Added two new indexing algorithms HNSW SQ and HNSQ BQ
  
  When to use each option?

  HNSW SQ: Best choice when you want a balance between saving memory and getting very precise results.
  HNSW BQ: Best choice when you need to save as much memory as possible at the cost of accuracy. Ideal for large scale datasets.

  Where to select?

  Available in Indexing Algorithms dropdown on Indexing Startegy page
  ![Indexing Algorithms](./images/Indexing_Algorthm_HNSW_BQ_SQ.png?raw=true)

- Introduced Hierarchical Chunking option in the Chunking Strategy dropdown menu

  Hierarchical chunking organizes information into smaller, nested pieces (child chunks) within larger, broader pieces (parent chunks). You can define:

  - Parent Chunk Size: The size of the broader chunks.
  - Child Chunk Size: The size of the smaller chunks.
  - Chunk Overlap Percentage: The shared content between consecutive child chunks to ensure context continuity.

  During retrieval, the system first fetches child chunks and swaps them with their corresponding parent chunks to provide a more complete understanding of the content. This ensures a balance between precision and context for optimal retrieval performance.

  When to use?
  - Ideal for Long structured documents (e.g., manuals, research papers)
  - For Summarization where complete understanding of context is needed

  Where to select?

  Available in Chunking dropdown on Indexing Startegy page
  ![Hierarchical Chunking](./images/Hierarchical_Chunking.png?raw=true)


- Integrated Re-Ranking capability

  Re-ranking is an optional step in the RAG pipeline that can significantly improve the quality of the generated output.

  Retrieval without Re-ranking:

  - Documents are retrieved from the vector store.
  - These documents are then fed directly to the generative model, which generates an output based on the information it finds in these documents.

  Retrieval with Re-ranking:

  - Documents are retrieved from the vector store.
  - A re-ranking model then analyzes these documents and reorders them based on their relevance to the query.
  - The reordered documents are then fed to the generative model, which generates an output based on the information it finds in these documents.

  Supported Re-Ranking models:
  - Amazon Rerank 1.0
  - Cohere Rerank 3.5

  Supported Regions:
  - us-west-2

  Where to select?
  ![ReRanking](./images/ReRanking.png?raw=true)


### Enhancements
- Experiment Parallelization

  - In previous versions, experiments with different models (across indexing, retrieval, and evaluation) could run in parallel, but experiments using the same model were limited to sequential execution.
  - In v1.0.2, this limitation is removed, allowing multiple experiments per model to run concurrently. This significantly accelerates overall project completion time.

- Valid Experiments are now processed asynchronously.

- Breadcrumbs are now included in the header section.

### Bug Fixes

- Resolved an issue where inferencing LLM details were not visible in the Experiment Details popup.  
- Updated the Experiment Details popup to ensure responsiveness.  

### Known Issues

- Missing error handling when a corrupted pdf file is uploaded.
- Discrepancy between directional pricing and estimated cost in few scenarios.
- The Valid Experiments page experiences delays when uploading large datasets or selecting all hyperparameters.
- The Titan embeddings G1 model displays an estimated cost of $0 in evaluation metrics.
- NAN values are being populated for faithfulness in the evaluation metrics.
- Validation messages for certain fields on the UI are incorrect.