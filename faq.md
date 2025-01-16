# Frequently Asked Questions

## 1. What is FloTorch.ai? What are its service offerings?

FloTorch.ai is an innovative platform designed to simplify and optimize the selection and configuration of Large Language Models (LLMs) for use in Retrieval Augmented Generation (RAG) systems. It addresses the challenges of manual evaluation, resource-intensive experimentation, and complex performance comparisons by providing an automated, user-friendly approach to decision-making. The platform enables efficient and cost-effective utilization of LLMs, making it a valuable tool for startups, researchers, developers, and enterprises.

### Service Offerings of FloTorch.ai:

- **Automated Evaluation of LLMs**
  - FloTorch.ai analyzes multiple LLM configurations by evaluating combinations of hyperparameters specified by users.
  - It measures key performance metrics such as relevance, fluency, and robustness.
- **Performance Insights**
  - Provides detailed performance scores for each evaluated LLM configuration.
  - Offers actionable insights into execution times and pricing, helping users understand the cost-effectiveness of each setup.
- **Cost and Time Efficiency**
  - Streamlines the LLM selection process by eliminating manual trial-and-error.
  - Saves time and resources by automating comparisons and evaluations.
- **User-Friendly Decision-Making**
  - Helps users make data-driven decisions aligned with their specific goals and budgets.
  - Simplifies the complexity of optimizing LLMs in RAG systems.
- **Broad Applicability**
  - Caters to diverse use cases, such as enhancing customer experiences, improving content generation, and refining data retrieval processes.
- **Targeted Support for Users**
  - Designed for startups, data scientists, developers, researchers, and enterprises seeking to optimize AI-driven systems.

By focusing on performance, cost, and time efficiency, FloTorch.ai empowers users to maximize the potential of generative AI without the need for extensive experimentation.

---

## 2. Is an API key required to be able to use this tool?

It is a platform hosted on AWS infrastructure and provides web-based access through an App Runner instance; it is common for such systems to require authentication mechanisms for secure access.

### For Web-Based Access:

After the installation is complete, users receive a web URL and credentials to log into the FloTorch application. This implies that secure login credentials (possibly including an API key or token) are required for authentication.

### For Programmatic Access:

If FloTorch.ai provides an API for external integrations, it is likely that credentials would be required to authenticate API calls.

### AWS Infrastructure:

Since FloTorch runs on AWS, users must have their AWS credentials configured locally to deploy and manage infrastructure. This is separate from accessing the FloTorch application itself.

---

## 3. Can I run this tool from a local machine, or do I have to necessarily use an EC2 instance?

FloTorch.ai is designed primarily for deployment on AWS infrastructure, including the use of an EC2 instance for setup and hosting. However, whether it can be run from a local machine depends on the specific requirements of the tool and the intended use case.

---

## 4. Is there any sample data available for use as knowledge base data and ground truth data?

FloTorch.ai includes sample data for knowledge base data and ground truth data. However, FloTorch typically provides some form of example datasets or pre-configured templates to help users get started.

---

## 5. Do I require AWS account access as a root user to be able to use the features and to be able to get the tool running?

No, you do not require root user access to an AWS account to use and set up FloTorch.ai. However, you do need an AWS account with sufficient permissions to perform specific actions necessary for deploying and managing the infrastructure. Using the root account directly is not recommended for security reasons. Instead, you should use an IAM user or role with the required permissions.

---

## 6. Who can help me in troubleshooting the errors I get in the tool?

If you encounter errors while using FloTorch.ai, there are several avenues to seek help and resolve the issues:

- Check the installation guide, FAQs, and other resources provided in the FloTorch repository or official website.
- Review detailed error logs (if available) for clues. The application may log specific issues during infrastructure setup or usage.

---

## 7. Can I contact someone or is there a way of getting some online support?

### Support Channels

- **GitHub Repository:**
  - If the tool is hosted on GitHub (e.g., FissionAI/FloTorch), check for an "Issues" tab.
  - You can report bugs or errors by creating a new issue with detailed information.
- **FloTorch.ai Website**

---

## 8. What is evaluation? What does the evaluation process do?

Evaluation refers to the process of analyzing the performance of the experiments conducted using Large Language Models (LLMs) for Retrieval Augmented Generation (RAG) tasks. The evaluation process measures how effectively the selected configurations and models meet specific criteria, such as relevance, fluency, robustness, and cost efficiency.

### Evaluation Process:

- **Metrics Assessment:**
  - Faithfulness
  - Context Precision
  - Aspect Critic
  - Answer Relevancy
- **Cost and Time Analysis**
- **Configuration Validation**
- **Result Visualization**
- **Iterative Improvement**

---

## 9. What is the data strategy and what is the retrieval strategy?

Data strategy and retrieval strategy are key components in configuring and optimizing experiments involving RAG systems.

---

## 10. Is there a limit on the size of the files I can upload?

Yes, the Knowledge Base dataset size limit is restricted to **40MB**.

---

## 11. I want to contribute to the GitHub source code of FloTorch.ai. Is there a way in which I can contribute?

[GitHub Repository](https://github.com/your-username/FloTorch.git)

---

## 12. Can I use this tool for commercial purposes?

This tool is governed by the terms and conditions of the **APACHE 2.0 license**.

---

## 13. When will this tool support SageMaker models?

It will be released shortly. Please stay tuned to the FloTorch.ai website for regular updates.

---

## 14. What is the meaning of directional pricing? Is it not accurate?

Directional pricing is an effective price taken for an experiment to complete. It is the summation of OpenSearch price, embedding model price, retrieval, and evaluation price.

---

## 15. Is there a limit on the number of experiments I can run with this tool?

Yes, here are restrictions from the tool:

1. KB dataset limit - **40MB**
2. GT questions - **50**
3. Max number of experiments - **25**

---

## 16. When is the next version of the tool going to be released?

The next version of the product will be released shortly. Stay tuned to the FloTorch.ai website for regular updates.

---

## 17. How much time does it take to complete an experiment with a typical configuration?

The time it takes to complete an experiment in FloTorch.ai with a typical configuration can vary based on several factors, including the complexity of the configuration, the size of the data, the type of model used, and the available computational resources.

---

## 18. Is there a default configuration available in the GitHub repository?

No, we do not have any default configuration available in Git.

---

## 19. Is the data which I use (project data and evaluation data) transferred to the cloud or made public?

No, it will be saved in an S3 bucket, but it is not made public. It will be limited to your AWS Account based on your default IAM configurations and Security Group settings.

---

## 20. What is the licensing mechanism for this tool?

The license is **Apache 2.0**.