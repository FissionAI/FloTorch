export const useTooltipInfo = {
    name: 'Project Name',
region: 'Specify the region where your AWS compute resources are hosted.',
kb_data: 'Upload or specify the knowledge base (documents, FAQs, etc.) that the application will use for retrieving relevant information.',
gt_data: 'Provide a reference dataset or accurate responses to evaluate the model\'s performance and accuracy.',
chunking_strategy: 'Select the method for dividing input documents into smaller, manageable sections.',
chunk_size: 'Define the maximum size (in tokens) of each chunk to optimize retrieval accuracy and performance.',
chunk_overlap: 'Set the number of overlapping tokens or words between adjacent chunks to maintain context continuity.',
embedding: 'Choose whether you want the language model from the Amazon Bedrock or Sagemaker family.',
vector_dimension: 'Set the dimensionality of the vector embeddings generated for document chunks.',
indexing_algorithm: 'Select the algorithm for organizing and searching vector embeddings efficiently.',
numberOfChunksRetrieved: 'Specify how many of the most relevant chunks should be retrieved for response generation.',
n_shot_prompts: 'Define the number of examples to include in the prompt for the model during few-shot learning tasks.',
knn_num: 'Set the number of nearest neighbours to consider when searching for similar embeddings in the vector index.',
temp_retrieval_llm: 'Adjust the randomness of the model\'s output. Higher values produce more diverse outputs, while lower values yield more focused responses.',
retrieval: "Select the language model used to retrieve and generate responses based on the retrieved chunks from the Amazon family.",
rerank_model_id: "Select an Amazon Bedrock model to reorder and refine search results from your vector store based on relevance."
}
