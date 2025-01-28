# What is FloTorch?

FloTorch is an innovative product poised to transform the field of Generative AI by simplifying and optimizing the decision-making process for leveraging Large Language Models (LLMs) in Retrieval Augmented Generation (RAG) systems. In today’s fast-paced digital landscape, selecting the right LLM setup is critical for achieving efficiency, accuracy, and cost-effectiveness. However, this process often involves extensive trial-and-error, significant resource expenditure, and complex comparisons of performance metrics. Our solution addresses these challenges with a streamlined, user-friendly approach.

**Latest Update**: FloTorch now supports Bedrock knowledge bases and DeepSeek-R1-Distill-Llama-8B model on Sagemaker.

## Key Features

- **Automated Evaluation of LLMs**: FloTorch evaluates multiple LLMs by analyzing combinations of hyperparameters defined by the end user.
- **Performance Metrics**: Produces detailed performance scores, including relevance, fluency, and robustness.
- **Cost and Time Insights**: Provides actionable insights into the pricing and execution times for each LLM configuration.
- **Data-Driven Decision-Making**: Empowers users to align LLM configurations with specific goals and budget constraints.

## Who Benefits from FloTorch?

FloTorch caters to a broad spectrum of users, including:

- **Startups**: Optimize AI-driven systems for rapid growth.
- **Data Scientists**: Simplify model selection and evaluation.
- **Developers**: Focus on deployment and innovation rather than experimentation.
- **Researchers**: Gain insights into LLM performance metrics effortlessly.
- **Enterprises**: Enhance customer experiences, improve content generation, and refine data retrieval processes.

## Why Choose FloTorch?
- **Well-Architected framework**: Focuses on five pillars of service architecture: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization.
- **Maximizes Efficiency**: Ensures users achieve the best performance from their chosen LLMs in less time as multiple experiments can run parallelly.
- **Eliminates Complexity**: No more manual evaluations or tedious trial-and-error processes.
- **Accelerates Selection**: Streamlines the evaluation and decision-making process.
- **Focus on Innovation**: Allows users to dedicate resources to innovation and deployment rather than experimentation.

![FloTorch Architecture](./flotorch-arch.png)

## Vision

By combining advanced evaluation capabilities with a focus on cost and time efficiency, FloTorch provides a holistic solution for navigating the evolving RAG landscape. It empowers users to focus on innovation and deployment, setting a new standard for intelligent decision-making in AI-driven applications.

With FloTorch, we aim to be a pivotal enabler of progress in the generative AI ecosystem, helping our users achieve excellence in their projects.

# Using FloTorch

## Demo

[![FloTorch Demo](./cover-image.png?raw=true)](https://fissiontorch-public.s3.us-east-1.amazonaws.com/demo.mp4)

## Installation guide

Please refer to our [Installation guide](install.md) for the installation steps in detail.

## Usage guide

Use our [usage guide](usage_guide.md) for more details on using FloTorch.
Click [here](faq.md) for frequently asked questions.

# Open Source Developer Contribution Guidelines

This document outlines the guidelines for contributing to the project to maintain consistency and code quality.

### Master Branch

- The `master` branch is the primary branch and should remain stable.
- **Avoid pushing directly to the `master` branch.** All changes must go through the pull request process.

### Feature Branches

- All new feature branches must be created from the `master` branch.
- Use descriptive names for feature branches.  
  Example: `feature/bedrock_claude_inferencer`

### Pull Requests

- All code changes must be submitted as pull requests.
- Each pull request should be reviewed by at least one other developer.
- Keep pull requests small and focused on a specific feature or fix.
- Include relevant information in commit messages to provide context.

### Branch Hygiene

- Delete feature branches after they have been successfully merged into `master`.

### Testing Changes Locally

- Before submitting a pull request, thoroughly test your changes locally to ensure they work as expected.

### Naming Conventions

- Use **snake_case** for:
  - names
  - Configuration variables
  - python file names
    Example: `example_snake_case`
