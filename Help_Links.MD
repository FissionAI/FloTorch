# Help Documentation

Welcome to the help documentation for this project. Below are the main sections and links for quick navigation.

## Table of Contents

- [Project Name](#projectname)
- [Region](#region)
- [Knowledge Base Data](#knowledge-base-data)
- [Ground Truth Data](#ground-truth-data)
- [Chunking](#chunking)
- [Chunk Size](#chunking-size)
- [Chunk Overlap Percentage](#chunk-overlap-percentage)
- [Embedding Model](#embedding-model)
- [Vector Dimensions](#vector-dimensions)
- [Indexing Algorithm](#indexing-algorithm)
- [N Shot Prompts](#n-shot-prompts)
- [KNN](#knn)
- [Reranking Model](#reranking-model)
- [Inferencing Model](#inferencing-model)
- [Inferencing Model Temperature](#inferencing-model-temperature)
- [Guardrals](#guardrails)
- [Evaluation](#evaluation)
- [Service](#service)
- [Embedding LLM](#embedding-llm)
- [Inference LLM](#inference-llm)

---

## Project Name

Project Name

## Region

AWS hosts different regions and avaibility zones in its infrastructure. When FloTorch users select particular zone such as US-East1 or US_West2

## Knowledge Base Data

In the context of Retrieval Augmented Generation (RAG), a "knowledge base" refers to a repository of structured information, like documents, data sets, or articles, that a large language model can access and retrieve relevant data from to enhance its responses to user queries, providing more accurate and contextually relevant answers based on specific, up-to-date information not necessarily included in its initial training data.

## Ground Truth Data

"Ground Truth Data for RAG systems using LLMs refers to a dataset of validated question-answer pairs that serve as a benchmark for evaluating and improving the performance of the RAG system14. This dataset typically includes:
Questions: Representative of user queries the system is expected to handle
Correct answers: Validated responses that are deemed accurate and complete
Relevant context: The information used to generate the correct answer
RAG system outputs: The answers produced by the RAG pipeline for comparison"

## Chunking

"Chunking in Retrieval Augmented Generation (RAG) systems using Large Language Models (LLMs) is the process of dividing large documents or text corpora into smaller, manageable segments called chunks. This technique is crucial for optimizing the performance of RAG systems, which combine information retrieval with language generation to produce more accurate and contextually relevant responses.

### Key Aspects of Chunking in RAG

Purpose: Chunking enhances the efficiency and accuracy of the retrieval process, which directly impacts the overall performance of RAG models.
Improved Retrieval: By breaking down information into smaller units, chunking allows for faster and more precise identification of relevant content.
Enhanced Generation: Well-defined chunks provide the generator with necessary context, leading to more coherent and contextually rich responses.
Scalability: Chunking enables efficient management of massive datasets, as each chunk can be individually indexed and maintained.

### Common Chunking Strategies

Fixed-size Chunking: Divides text into uniform chunks based on a predefined character count.Currently fixed-size chunking is supported in FloTorch.
Semantic Chunking: Breaks text into semantically coherent segments, preserving contextual integrity.
Token-based Chunking: Segments text based on a specific number of tokens, which is particularly useful for LLMs with token limits.
Hierarchical Chunking: Hierarchical chunking is an advanced technique used in Retrieval-Augmented Generation (RAG) systems to optimize the processing of large datasets. This method involves dividing documents into multiple levels of chunks, typically ranging from larger to smaller sizes Currently hierarchical chunking is supported in FloTorch.
Effective chunking is essential for RAG systems as it directly influences retrieval precision, response quality, and computational efficiency3. The choice of chunking strategy depends on factors such as document structure, application requirements, and the desired balance between semantic integrity and processing speed."

## Chunk Size

"Chunk size in RAG (Retrieval Augmented Generation) systems refers to the number of words or tokens used to divide large documents into smaller, manageable segments for efficient information retrieval. It is a critical parameter that significantly impacts the performance and effectiveness of RAG systems.

### Chunk size matters for several reasons:

Relevance and granularity: Smaller chunk sizes (e.g., 128 tokens) provide more granular information but risk missing vital context. Larger sizes (e.g., 512 tokens) often capture more comprehensive information1.
Retrieval accuracy: Smaller chunks allow for more precise matching and retrieval of relevant information, improving the system's ability to find specific details8.
Context preservation: Larger chunks provide broader context, which can be beneficial for tasks requiring more comprehensive understanding2.
Computational efficiency: Smaller chunks generally lead to faster retrieval times, but too many small chunks can increase search complexity.
Response quality: The chunk size affects the faithfulness and relevancy of the generated responses. Studies have shown that a chunk size of 1024 tokens can provide an optimal balance between response time and quality.

### The ideal chunk size varies depending on factors such as:

The nature and structure of the source documents
The specific task or query types
The desired balance between precision and context
The computational resources available
We suggest starting with a chunk size of around 256 tokens (approximately 1024 characters) and then experimenting to find the optimal size for a specific use case. It's important to note that chunk sizes can vary within a dataset, allowing for flexibility based on the information density of different sections or paragraphs."

## Chunk Overlap Percentage

"Chunk percentage overlap refers to the proportion of content shared between consecutive text chunks when a document is split for indexing and retrieval. It's a crucial parameter that impacts both the indexing process and the quality of information retrieved.

### How Chunking and Overlap Work?

Document Splitting: A large document is divided into smaller, manageable units called ""chunks."" These chunks are the units of information that the RAG system will retrieve.

Overlap: Instead of creating chunks with completely distinct content, a certain percentage of text is shared or overlapped between adjacent chunks. For example, a 20% overlap means that the last 20% of a chunk is identical to the first 20% of the following chunk.

### Impact on Indexing:

Increased Redundancy: Overlapping chunks introduce redundancy into the index. The same content is indexed multiple times (across different chunks). This increases the size of the index.

More Comprehensive Context: Overlap ensures that important contextual information isn't lost at chunk boundaries. If a sentence or key phrase spans across two chunks, the overlap ensures that both chunks contain enough context to be meaningful.

Improved Retrieval: During retrieval, the query might match content within the overlapping portion of two chunks. This increases the chances of retrieving relevant information, even if the most relevant sentence is split across chunks. "

## Embedding Model

"An embedding model in RAG systems is a specialized neural network that converts text (documents, queries, or sentences) into dense numerical vectors - essentially mapping words and phrases into points in a high-dimensional space. These models serve dual purposes in RAG: converting knowledge base documents into vector representations and transforming user queries into the same vector space. This allows the system to find relevant documents by measuring the similarity between the query vector and document vectors in this mathematical space.
The choice of embedding model significantly impacts RAG system performance through several key factors. Better models capture more nuanced semantic relationships, leading to more accurate document retrieval. Domain-specific models (like those trained on medical or legal text) often outperform general-purpose embeddings in specialized fields. Additionally, practical considerations like dimensionality, computational requirements, language support, and cost all influence the selection. "

## Vector Dimensions

"Vector dimensions in RAG (Retrieval Augmented Generation) systems refer to the size or length of the numerical vectors that represent text or other data after being processed by an embedding model. For example, OpenAI's text-embedding-3-small model produces vectors with 1536 dimensions, while some other models might create vectors with 384 or 768 dimensions. Each dimension captures different semantic features of the input text, with higher-dimensional vectors generally capable of representing more nuanced semantic relationships, though this comes with increased computational and storage costs.
The choice of embedding model and its vector dimensions has significant implications for both system performance and resource requirements. Higher-dimensional vectors typically provide better semantic representation and can lead to more accurate similarity searches, but they require more storage space in vector databases and more computational resources for similarity calculations. For instance, a vector database storing millions of 1536-dimensional vectors will need substantially more storage space and memory compared to one storing 384-dimensional vectors. This trade-off between representation quality and resource efficiency is particularly important when scaling RAG systems to handle large document collections.
Vector databases are specifically optimized to handle these high-dimensional vectors efficiently, using specialized indexing techniques like HNSW (Hierarchical Navigable Small World) or IVF (Inverted File Index) to enable fast similarity searches. The dimensionality of the vectors directly impacts the index size and search performance. For example, Pinecone, Weaviate, and other vector databases often recommend specific index configurations based on the vector dimensions of your chosen embedding model. When selecting an embedding model, it's crucial to consider not just the raw accuracy metrics but also how well your chosen vector database can handle the resulting vector dimensions in terms of both search performance and cost efficiency."

## Indexing Algorithm

"HNSW (Hierarchical Navigable Small World) is a graph-based algorithm for finding approximate nearest neighbors (ANN), crucial for tasks like document retrieval in RAG systems. It constructs a multi-layered graph where each layer represents the data at different granularities. The top layer is sparse with long-range connections for fast coarse search, while lower layers become progressively denser with shorter-range connections for refined local search. When inserting a new data point, it's connected to its nearest neighbors in each layer, creating a ""navigable small world"" structure.

Searching starts at a random point in the top layer and navigates down to the bottom layer, following connections to closer neighbors at each level. This hierarchical approach allows for efficient exploration of the data space. At the bottom layer, a final search among candidate neighbors yields the approximate nearest neighbors. HNSW is particularly useful in RAG because it efficiently finds similar vector embeddings, representing documents and queries, enabling fast retrieval of relevant context for generating responses.

Key features: Hierarchical structure, navigable small world connections, approximate nearest neighbors, scalability, dynamic updates.
RAG relevance: Efficient retrieval of similar document embeddings for context retrieval, crucial for fast and accurate response generation."

## N Shot Prompts

"
Yes, N-shot prompting can work in Retrieval-Augmented Generation (RAG) systems, but its effectiveness depends on the use case. Here’s how it applies:

### How N-Shot Prompting Works in RAG

RAG involves retrieving relevant documents and then using a language model (LLM) to generate responses. You can enhance RAG with N-shot prompting by including relevant examples in the prompt before passing it to the model.

### Key Considerations for N-Shot in RAG

Example Relevance – The selected examples should closely resemble the query or demonstrate the expected response format.
Token Limitations – More examples mean a longer prompt, potentially reducing room for retrieved context.
Balancing Retrieval and Prompting – If retrieval is strong, fewer examples may be needed. If retrieval is weak, more examples might help guide the response.

### How Many Examples for N-Shot?

1-shot – Useful when examples provide structured guidance without overwhelming the model.
2-3 shot – Effective for complex or nuanced queries where variations matter.
More than 3 – Only viable if you have enough token space and the task benefits from multiple examples. Currently not supported in FloTorch."

## KNN

"K-Nearest Neighbors (KNN) parameter determines how many documents or embeddings are retrieved from the vector database before being passed to the language model for answer generation. Choosing the right value for K is crucial because it impacts accuracy, cost, and latency. A higher K increases the chances of retrieving relevant context, improving accuracy, but also raises computational cost and response time. Conversely, a lower K reduces retrieval noise and speeds up inference but may omit important information.

### Key Impacts of KNN Parameter:

Answer Accuracy:
Higher K provides more context but may introduce irrelevant data, diluting precision.
Lower K ensures focused retrieval but risks missing critical information.
Cost Considerations:
More retrieved documents mean higher computational cost in vector search and LLM token processing.
Optimal K balances quality and efficiency to avoid unnecessary API or compute expenses.
Latency & Performance:
Large K values increase processing time in retrieval and model inference.
Smaller K speeds up response but may compromise completeness.
A good approach is experimenting with different K values (e.g., K=3, K=5, K=10) and evaluating answer relevance against cost and latency trade-offs. Adaptive K selection, where K varies based on query complexity, can further optimize results."

## Reranking Models

"Reranking models serve several key purposes:

Initial retrieval limitations: Vector similarity search (like embedding-based retrieval) can miss semantically relevant results since it primarily captures high-level semantic similarity. For example, if you search for ""What causes headaches?"", vector search might return passages about general pain rather than headache-specific information.
Quality refinement: Rerankers can consider more nuanced aspects of relevance by:

Looking at exact term matches and word order
Understanding question-answer relationships better
Considering document structure and context
Evaluating factual alignment

To determine if you need reranking, evaluate these factors:

Quality Assessment:

Run sample queries and check if the initial retrieval results are sufficiently relevant
Look for cases where obviously relevant documents are ranked too low
Check if the results contain too many false positives
Task Characteristics:
High-precision requirements (medical, legal) → Likely need reranking
Simple keyword-based queries → Might not need reranking
Complex questions requiring inference → Would benefit from reranking

Cost-Benefit Analysis:

Consider computational overhead - reranking adds latency
Evaluate if accuracy improvement justifies additional complexity
Consider available resources (compute, time, budget)"

## Inferencing Model

"How do you select the right inferencing model for your RAG system?
Here's a systematic approach:
First, consider your key requirements:

1. Response speed needed (latency requirements)
2. Cost constraints and budget
3. Accuracy requirements
4. Context window size needed for your documents
5. Whether you need specialized knowledge in certain domains
6. Deployment constraints (on-premise vs cloud)

Evaluation methodology:

Instead of choosing a model based on general benchmarks alone, we recommend:

1. Creating a representative test set from your actual data and uploading it in FloTorch
2. Defining clear evaluation metrics relevant to your use case (accuracy, consistency, relevance)
3. Running controlled A/B tests with different models using FloTorch

Specific model selection strategies:

1. Start with smaller models (like Mistral 7B or Llama 3 ) as baselines
2. Test mid-size models (like Nova Lite, Claude Haiku or GPT-3.5) for balance of performance/cost
3. Only move to larger models (like Nova Pro, GPT-4 or Claude Opus) if smaller ones don't meet requirements
4. Consider fine-tuning smaller models on your domain if you have enough data on SageMaker or similar.

Key metrics to track:

1. Answer relevance (Supported in FloTorch)
2. Contenxt Precision (Supported in FloTorch)
3. Response consistency
4. Hallucination rate (Check actual answers and ground truth in FloTorch)
5. Latency per query (look at inferencing time)
6. Cost per query (look at cost breakdown)

Practical tips:

1. Run separate evaluations for different query types
2. Test with different prompt templates
3. Measure performance with different retrieval counts
4. Consider hosting costs and infrastructure requirements
5. Test model performance with and without retrieved context"

## Inferencing Model Temperature

"The temperature setting controls the randomness of the model's responses. A lower temperature (e.g., 0 to 0.3) makes the model more deterministic, meaning it will stick closely to retrieved documents and produce highly factual, consistent answers. A higher temperature (e.g., 0.7 or higher) increases diversity and creativity, making responses more exploratory but also introducing a higher risk of hallucinations. For RAG applications focused on accuracy and reliability, such as legal or financial question-answering, keeping the temperature low is typically best. Conversely, for brainstorming or content generation, a higher temperature can be useful.

The choice of temperature impacts multiple aspects of the system:

Accuracy: Lower temperatures improve factual consistency by reducing randomness, making the model adhere closely to retrieved data.
Cost: A lower temperature may reduce token usage in iterative calls (fewer retries for corrections), but temperature itself doesn’t directly affect API costs.
Latency: Lower temperatures can lead to faster response times, as deterministic outputs require fewer adjustments, whereas high-temperature responses may generate longer or more variable outputs.
For most enterprise RAG systems, where factual correctness is critical, a temperature between 0.0 and 0.2 is generally recommended."

## Guardrails

"Safety guardrails are essential for RAG systems to ensure the accuracy, reliability, and ethical use of AI-generated content. These guardrails help mitigate several risks:
Prevent hallucinations and factual errors.
Block undesirable and harmful content
Protect user privacy by filtering out personal information
Ensure contextual integrity and relevance of responses
Maintain compliance with responsible AI policies

Several providers offer guardrail services for RAG systems:
NVIDIA NeMo Guardrails: A toolkit and microservice for integrating security layers into RAG applications1.
Amazon Bedrock Guardrails: Provides configurable safeguards for building generative AI applications at scale, offering industry-leading safety protections. Bedrock Guardrails are already supported in FloTorch.
Llama-Guard: An advanced guardrail model that evaluates content after the retrieval and generation phases.

These guardrail services help enterprises strike a balance between delivering relevant content and ensuring real-time responses while maintaining safety and security in their RAG applications"

## Evaluation

"RAG (Retrieval-Augmented Generation) systems can be evaluated using various metrics to assess their performance and reliability. Here are some key evaluation metrics:
Retrieval Metrics
Context Relevance: Measures whether retrieved passages are relevant to the query (0-1 scale).
Context Recall: Evaluates how well retrieved context matches the ground truth answer (0-1 scale).
Context Precision: Assesses if relevant information is ranked highly in the retrieved context (0-1 scale).
Generation Metrics
Faithfulness: Measures the integrity of the answer relative to retrieved contexts.
Answer Relevancy: Evaluates the relevance of the generated answer to the original query.
Answer Correctness: Assesses alignment with reference answers.
Completeness: Evaluates if the answer covers all aspects of the query.
Harmfulness: Checks for potentially harmful content in responses.
Answer Refusal: Monitors instances where the system declines to answer.
Stereotyping: Assesses for biased or stereotypical content in responses.
RAGAS Evaluation
RAGAS (RAG Assessment) is a comprehensive evaluation framework that:
Uses a dataset of questions, ideal answers, and relevant context.
Compares generated answers with ground truth.
Provides metrics like faithfulness, relevance, and semantic similarity.
Assesses both retrieval and answer quality.
Amazon Bedrock LLM-as-a-Judge Evaluation
Amazon Bedrock offers an LLM-as-a-Judge capability for RAG evaluation:
Allows automatic knowledge base evaluation for RAG applications.
Uses an LLM to compute evaluation metrics.
Enables comparison of different configurations and tuning settings.
Offers metrics for both retrieval and generation, including correctness, completeness, and faithfulness.
Incorporates responsible AI metrics like harmfulness and stereotyping.
Provides a cost-effective and time-efficient alternative to human evaluations.

These evaluation methods help in optimizing RAG systems by identifying areas for improvement in both retrieval and generation components, ensuring accurate, relevant, and reliable responses."

## Service

## Embedding LLM

## Inference LLM

Once installed, run the project by using the following command:

```bash
./start_project
```
