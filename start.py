from lambda_handlers.indexing_handler import lambda_handler as indexing
from lambda_handlers.retriever_handler import lambda_handler as retriever
from lambda_handlers.evaluation_handler import lambda_handler as evaluation

from core.service.experimental_config_service import ExperimentalConfigService
from config.config import Config
from retriever.retriever import retrieve

if __name__ == "__main__":
    input_data = {
        "experiment_id": "MMN5SF0D", #"TIK045O5", #"ZWSZ9V7E", #"OVUBX9SQ", #evaluation - #"2H2AOWFH", #"POCFEEOA", #"946RI6BP"
        "execution_id": "50UQ1",
        "gt_data": "s3://s3-test-bucket-kiran/medical_q&a_10.json",
        "chunking_strategy": "Fixed",
        "chunk_size": 500,
        "chunk_overlap": 50,
        "vector_dimension": 1024,
        "indexing_algorithm": "hnsw",
        "index_id": "kiran-local-index",
        "n_shot_prompts": 0,
        "knn_num": 5,
        "temp_retrieval_llm": 0.7,
        "embedding_model": "amazon.titan-embed-text-v2:0",
        "retrieval_model": "meta-textgeneration-llama-3-1-8b-instruct",
        "kb_data": "",
        "aws_region": "us-east-1",
        "embedding_service": "bedrock",
        "retrieval_service": "sagemaker",
        "llm_based_eval": "True", # llm_based_eval: bool = True
        "eval_service": "ragas",
        "eval_embedding_model": "amazon.titan-embed-text-v1", #"amazon.nova-pro-v1:0",
        "eval_retrieval_model": "mistral.mixtral-8x7b-instruct-v0:1",
        "hierarchical_child_chunk_size": 128,
        "hierarchical_parent_chunk_size": 512,
        "hierarchical_chunk_overlap_percentage": 5,
        "n_shot_prompt_guide_obj": {
        "system_prompt" : "You are an expert medical practitioner. Classify the following medical diagnosis into one of these 5 categories: neoplasms, digestive system diseases, nervous system diseases, cardiovascular diseases, or general pathological conditions. Provide your response in this exact format, with no additional text or repetition:\ndisease: [Single disease category]\ncontext: [Brief explanation in 1-2 sentences, maximum 50 words]\nconfidence: [Single number between 0-100]\nDo not repeat any information. Provide only one disease, one context explanation, and one confidence score. Any deviation from this format or repetition will be considered an error. Make sure the disease, context and confidence are in the final answer and not in your thoughts",
        "examples" : [
            {
                "example" : "Thrombotic thrombocytopenic purpura treated with high-dose intravenous gamma globulin. Plasma infusion and/or plasma exchange has become standard therapy in the treatment of thrombotic thrombocytopenic purpura (TTP). The management of patients in whom such primary therapy fails is difficult and uncertain. We have described a patient who obtained a sustained remission with the use of high-dose IV gamma globulin after an initial response to aggressive plasma exchange was followed by prompt relapse. Our case and others suggest that high-dose IV IgG may induce remission in patients with TTP who do not respond to standard plasma infusion and/or exchange. Answer: General pathological conditions"
            },
            {
                "example" : "Further notes on Munchausen's syndrome: a case report of a change from acute abdominal to neurological type. A rare case of Munchausen's syndrome beginning in early childhood is described. The diagnosis of Munchausen's syndrome was made at the age of 29 years, after the symptoms had changed from acute abdominal to neurological complaints, with feigned loss of consciousness, first ascribed to an encephalitis. Insight into the psychopathology of this patient is given by his biography, by assessment of a psychotherapist, who had treated him some years before, and by his observed profile in some psychological tests. Answer: Nervous system diseases"
            },
            {
                "example" : "Color Doppler diagnosis of mechanical prosthetic mitral regurgitation: usefulness of the flow convergence region proximal to the regurgitant orifice. In prosthetic or paravalvular prosthetic mitral regurgitation, transthoracic color Doppler flow mapping can sometimes fail to detect the regurgitant jet within the left atrium because of the shadowing by the prosthetic valve. To overcome this limitation, we assessed the utility of color Doppler visualization of the flow convergence region (FCR) proximal to the regurgitant orifice in 20 consecutive patients with mechanical prosthetic mitral regurgitation documented by surgery and cardiac catheterization (13 of 20 patients). In addition, we studied 33 patients with normally functioning mitral prostheses. Doppler studies were performed in the apical, subcostal, and parasternal long-axis views. An FCR was detected in 95% (19 of 20) of patients with prosthetic mitral regurgitation. A jet area in the left atrium was detected in 60% (12 of 20) of patients. In 18 of 19 patients with Doppler-detected FCR, the site of the leak was correctly identified by observing the location of the FCR. A trivial jet area was detected in eight patients with a normally functioning mitral prosthesis; in none was an FCR identified. Thus color Doppler visualization of the FCR proximal to the regurgitant orifice is superior to the jet area in the diagnosis of mechanical prosthetic mitral regurgitation. Moreover, FCR permits localization of the site of the leak with good accuracy. Answer: General pathological conditions"
            }
        ],
        "user_prompt" : "Categorize the following medical case into one of the 5 categories, adhering strictly to the format specified in the system prompt. Any repetition or deviation from the format will result in an incorrect response."
        },
        "bedrock_knowledge_base": False,
        "knowledge_base": False
    }

    #indexing(input_data, None)
    # retriever(input_data, None)
    evaluation(input_data, None)
    
# Load base configuration
# config = Config.load_config()


# exp_config = ExperimentalConfigService(config).create_experimental_config(input_data)
    
# # Execute retrieve method
# retrieve(config, exp_config)
