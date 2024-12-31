from math import cos
from aws_cdk import (
    Stack,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_dynamodb as dynamodb,
    aws_lambda as aws_lambda,
    aws_iam as iam,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_logs as logs,
    aws_lambda as lambda_,
    aws_ecr as ecr,
    CfnOutput,
    Duration,
    RemovalPolicy,
    Aws,
    SecretValue,
)
from constructs import Construct
from vpc.config import InfraConfig

class StateMachineStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc_stack, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Getting values from VPC Config
        infraConfig = InfraConfig()

        table_suffix = id.split('-')[-1]
        state_machine_name = f"FlotorchStateMachine-{table_suffix}"

        # Parameters from vpc_stack
        cluster = vpc_stack.ecs_cluster

        indexing_task_definition = vpc_stack.task_definitions["indexing"]
        retriever_task_definition = vpc_stack.task_definitions["retriever"]
        evaluation_task_definition = vpc_stack.task_definitions["evaluation"]

        indexing_container_name = indexing_task_definition.default_container.container_name
        retriever_container_name = retriever_task_definition.default_container.container_name
        evaluation_container_name = evaluation_task_definition.default_container.container_name

        region = Aws.REGION
        data_bucket_name = vpc_stack.data_bucket.bucket_name
        execution_table_name = vpc_stack.execution_table.table_name
        experiment_table_name = vpc_stack.experiment_table.table_name
        metrics_table_name = vpc_stack.metrics_table.table_name
        model_invocations_table_name = vpc_stack.model_invocations_table.table_name
        opensearch_endpoint = vpc_stack.opensearch_domain.domain_endpoint
        experiment_question_metrics_experiment_id_index = "experiment_id-index"

        private_subnets = vpc_stack.vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS).subnets
        security_groups = [vpc_stack.indexer_security_group]

        # Replace hardcoded password with SecretValue (ensure to store the actual password securely)
        opensearch_password = infraConfig.opensearch_admin_password  # Replace with actual secret management

        # Lambda Execution Role
        instance_role = iam.Role(
            self,
            f"opensearch-lambda-creation-role-{table_suffix}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )

        instance_role.add_to_policy(iam.PolicyStatement(
            actions=["es:*"],
            resources=[vpc_stack.opensearch_domain.domain_arn]
        ))

        instance_role.add_to_policy(iam.PolicyStatement(
            actions=["ec2:*"],
            resources=[vpc_stack.vpc.vpc_arn]
        ))

        # Add permissions for Lambda execution role
        # Cloudwatch, networkInterface
        instance_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=[
                    "*"
                ]
            )
        )

        instance_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "ec2:DescribeNetworkInterfaces",
                    "ec2:CreateNetworkInterface",
                    "ec2:DeleteNetworkInterface",
                    "ec2:DescribeInstances",
                    "ec2:AttachNetworkInterface"
                ],
                resources=[
                    "*"
                ]
            )
        )

        instance_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "es:*"
                ],
                resources=[
                    "*"
                ]
            )
        )

        # Create Lambda function
        lambda_function = lambda_.Function(
            self,
            f"OpenSearchLambda-{table_suffix}",
            function_name=f"OpenSearchLambda-{table_suffix}",
            runtime=lambda_.Runtime.FROM_IMAGE,
            code=lambda_.Code.from_ecr_image(
                repository=ecr.Repository.from_repository_name(
                    self,
                    f"RuntimeECRRepo-{table_suffix}",
                    repository_name=f"flotorch-runtime-{table_suffix}"
                ),
                tag="latest"
            ),
            handler=lambda_.Handler.FROM_IMAGE,
            vpc=vpc_stack.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[
                vpc_stack.opensearch_sg,
                vpc_stack.lambda_sg
            ],
            timeout=Duration.seconds(300),
            memory_size=1024,
            environment={
                "opensearch_host": vpc_stack.opensearch_domain.domain_endpoint,
                "opensearch_username": infraConfig.opensearch_admin_user,
                "opensearch_password": infraConfig.opensearch_admin_password,
                "vector_field_name": "vectors",
                "aws_region": self.region,
                "opensearch_serverless": "false"
            }
        )

        # IAM Role for State Machine
        state_machine_role = iam.Role(
            self, "StateMachineRole",
            assumed_by=iam.ServicePrincipal("states.amazonaws.com")
        )

        # Add policies to the state machine role
        # DynamoDB permissions
        state_machine_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:Scan",
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Query"
                ],
                resources=[
                    vpc_stack.experiment_table.table_arn,
                    vpc_stack.execution_table.table_arn,
                    vpc_stack.model_invocations_table.table_arn,
                    vpc_stack.metrics_table.table_arn,
                    f"{vpc_stack.experiment_table.table_arn}/index/*",
                    f"{vpc_stack.execution_table.table_arn}/index/*",
                    f"{vpc_stack.model_invocations_table.table_arn}/index/*",
                    f"{vpc_stack.metrics_table.table_arn}/index/*"
                ]
            )
        )

        # Lambda invocation permissions
        state_machine_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "lambda:InvokeFunction"
                ],
                resources=["*"]
            )
        )

        # ECS permissions
        state_machine_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "ecs:RunTask",
                    "ecs:StopTask",
                    "ecs:DescribeTasks",
                    "iam:PassRole"
                ],
                resources=["*"]
            )
        )

        # CloudWatch Logs permissions
        state_machine_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogDelivery",
                    "logs:GetLogDelivery",
                    "logs:UpdateLogDelivery",
                    "logs:DeleteLogDelivery",
                    "logs:ListLogDeliveries",
                    "logs:PutResourcePolicy",
                    "logs:DescribeResourcePolicies",
                    "logs:DescribeLogGroups"
                ],
                resources=["*"]
            )
        )

        # IAM permissions for task roles
        state_machine_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "iam:GetRole",
                    "iam:PassRole"
                ],
                resources=[
                    indexing_task_definition.task_role.role_arn,
                    retriever_task_definition.task_role.role_arn,
                    evaluation_task_definition.task_role.role_arn
                ]
            )
        )

        # Import existing Lambda function
        lambda_function = aws_lambda.Function.from_function_arn(
            self,
            "OpenSearchLambdaFunction",
            f"arn:aws:lambda:{Aws.REGION}:{Aws.ACCOUNT_ID}:function:OpenSearchLambda-{table_suffix}"
        )

        # Import existing Cost Lambda function
        cost_lambda_function = aws_lambda.Function.from_function_arn(
            self,
            "CostLambdaFunction",
            f"arn:aws:lambda:{Aws.REGION}:{Aws.ACCOUNT_ID}:function:FlotorchCostComputeLambda-{table_suffix}"
        )

        # Define the "InjectConfig" Pass state
        inject_config = sfn.Pass(
            self,
            "InjectConfig",
            parameters={
                "ClusterArn": cluster.cluster_arn,
                "IndexingTaskDefinitionArn": indexing_task_definition.task_definition_arn,
                "RetrieverTaskDefinitionArn": retriever_task_definition.task_definition_arn,
                "EvaluationTaskDefinitionArn": evaluation_task_definition.task_definition_arn,
                "IndexingContainerName": indexing_container_name,
                "RetrieverContainerName": retriever_container_name,
                "EvaluationContainerName": evaluation_container_name,
                "Region": region,
                "DataBucket": data_bucket_name,
                "ExecutionTable": execution_table_name,
                "ExperimentTable": experiment_table_name,
                "MetricsTable": metrics_table_name,
                "ModelInvocationsTable": model_invocations_table_name,
                "ExperimentQuestionMetricsExperimentIdIndex": experiment_question_metrics_experiment_id_index,
                "OpenSearchEndpoint": opensearch_endpoint,
                "OpenSearchUsername": "admin",
                "OpenSearchPassword": opensearch_password,
                "OpenSearchServerless": "false",
                "InferencePrompt": "Task: You are a medical expert tasked with categorizing medical cases. Based on the provided case abstract, you must assign the case to one and only one of the following 5 categories:\n\n1. Neoplasms\n2. Digestive System Diseases\n3. Nervous System Diseases\n4. Cardiovascular System Diseases\n5. General Pathological Conditions\n\nImportant Rules:\n\n1.Give only the category as response and no explanations.\n2.You must select exactly one of the five categories.\n3.Do not create new categories or use 'Other'.\n4.If the case could fit into multiple categories, select the category that represents the primary focus of the abstract.",
                "PrivateSubnets": [subnet.subnet_id for subnet in private_subnets],
                "SecurityGroups": [sg.security_group_id for sg in security_groups],
                "execution_id.$": "$.execution_id"
            }
        )

        # Define the "Query model invocations" task
        query_model_invocations_task = tasks.CallAwsService(
            self,
            "Query model invocations",
            service="dynamodb",
            action="scan",
            parameters={
                "TableName": model_invocations_table_name
            },
            iam_resources=[vpc_stack.model_invocations_table.table_arn],
            result_path="$.invocations"
        )

        # Define the "Clear model invocations table" task inside Map
        clear_model_invocations_table_task = tasks.CallAwsService(
            self,
            "Clear model invocations table",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": model_invocations_table_name,
                "Key": {
                    "execution_model_id": {
                        "S.$": "$.execution_model_id"
                    }
                },
                "UpdateExpression": "SET invocations = :myValueRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "N": "0"
                    }
                }
            },
            iam_resources=[vpc_stack.model_invocations_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        )

        # Define the Map state for clearing model invocations
        clear_invocations_map = sfn.Map(
            self,
            "Map",
            items_path="$.invocations.Items",
            result_path=sfn.JsonPath.DISCARD,
            parameters={
                "execution_model_id.$": "$$.Map.Item.Value.execution_model_id.S"
            }
        )
        clear_invocations_map.iterator(clear_model_invocations_table_task)

        # "Wait for model invocations to be cleared"
        wait_for_model_invocations_cleared = sfn.Wait(
            self,
            "Wait for model invocations to be cleared",
            time=sfn.WaitTime.duration(Duration.seconds(30))
        )

        # Define the "Query" task
        query_task = tasks.CallAwsService(
            self,
            "Query",
            service="dynamodb",
            action="query",
            parameters={
                "TableName": experiment_table_name,
                "IndexName": "execution_id-index",
                "KeyConditionExpression": "execution_id = :executionId",
                "ExpressionAttributeValues": {
                    ":executionId": {
                        "S.$": "$.execution_id"
                    }
                }
            },
            result_selector={
                "execution_id.$": "$.Items[0].execution_id",
                "Items.$": "$.Items"
            },
            result_path="$",
            iam_resources=[f"{vpc_stack.experiment_table.table_arn}/index/execution_id-index"]
        )

        # Define the "Create Opensearch indices" task
        create_opensearch_indices_task = tasks.LambdaInvoke(
            self,
            "Create Opensearch indices",
            lambda_function=lambda_function,
            payload=sfn.TaskInput.from_json_path_at("$"),
            result_path="$.indexCreation",
            input_path="$.Items"
        )
        create_opensearch_indices_task.add_retry(
            errors=[
                "Lambda.ServiceException",
                "Lambda.AWSLambdaException",
                "Lambda.SdkClientException",
                "Lambda.TooManyRequestsException"
            ],
            interval=Duration.seconds(30),
            max_attempts=3,
            backoff_rate=2,
            jitter_strategy=sfn.JitterType.FULL
        )

        # Define the "Run Cost Lambda function" task
        run_cost_lambda_function_task = tasks.LambdaInvoke(
            self,
            "Run Cost Lambda function",
            lambda_function=cost_lambda_function,
            payload=sfn.TaskInput.from_object({
                "experiment_id": sfn.JsonPath.string_at("$.parsedConfig.parsed_config.experiment_id"),
                "aws_region": sfn.JsonPath.string_at("$.parsedConfig.parsed_config.aws_region"),
                "embedding_model": sfn.JsonPath.string_at("$.parsedConfig.parsed_config.embedding_model"),
                "retrieval_model": sfn.JsonPath.string_at("$.parsedConfig.parsed_config.retrieval_model")
            }),
            result_path="$.costEstimation",
        )
        run_cost_lambda_function_task.add_retry(
            errors=[
                "Lambda.ServiceException",
                "Lambda.AWSLambdaException",
                "Lambda.SdkClientException",
                "Lambda.TooManyRequestsException"
            ],
            interval=Duration.seconds(30),
            max_attempts=3,
            backoff_rate=2,
            jitter_strategy=sfn.JitterType.FULL
        )

        # Define the "Index creation evaluation" Choice state
        index_creation_evaluation_choice = sfn.Choice(self, "Index creation evaluation")

        # Define the "Update Execution status" task
        update_execution_status_task = tasks.CallAwsService(
            self,
            "Update Execution status",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": execution_table_name,
                "Key": {
                    "id": {
                        "S.$": "$.Items[0].execution_id.S"
                    }
                },
                "UpdateExpression": "SET #val = :myValueRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "S": "completed"
                    }
                },
                "ExpressionAttributeNames": {
                    "#val": "status"
                }
            },
            iam_resources=[vpc_stack.execution_table.table_arn],
            result_path=sfn.JsonPath.DISCARD,
            output_path=sfn.JsonPath.DISCARD,
            comment="Update Execution status to completed"
        )

        # Define the "Experiments Map" Map state
        experiments_map = sfn.Map(
            self,
            "Experiments Map",
            items_path="$.Items",
            result_path=sfn.JsonPath.DISCARD,
            parameters={
                "id.$": "$$.Map.Item.Value.id.S"
            }
        )

        # Define the states inside the Experiments Map iterator
        # "Update experiment start time"
        update_experiment_start_time = tasks.CallAwsService(
            self,
            "Update experiment start time",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                    "id": {
                        "S.$": "$.id"
                    }
                },
                "UpdateExpression": "SET start_datetime = :timeRef, experiment_status = :status",
                "ExpressionAttributeValues": {
                    ":timeRef": {
                        "S.$": "$$.State.EnteredTime"
                    },
                     ":status": {
                       "S": "in_progress"
                    }
                }
            },
            iam_resources=[vpc_stack.experiment_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        )

        # "DynamoDB GetItem By id"
        dynamodb_get_item_by_id = tasks.CallAwsService(
            self,
            "DynamoDB GetItem By id",
            service="dynamodb",
            action="getItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                    "id": {
                        "S.$": "$.id"
                    }
                }
            },
            iam_resources=[vpc_stack.experiment_table.table_arn],
            result_path="$.Item"
        )

        # "Evaluate Indexing Model Check" Choice state
        evaluate_chunking_strategy_choice = sfn.Choice(self, "Evaluate Chunking Strategy")

        # "Extract config from experiment"
        extract_config_from_experiment = sfn.Pass(
            self,
            "Extract config from experiment",
            parameters={
                "parsed_config": {
                    "id.$": "$.Item.Item.id.S",
                    "index_id.$": "$.Item.Item.index_id.S",
                    "execution_id.$": "$.Item.Item.execution_id.S",
                    "experiment_id.$": "$.Item.Item.id.S",
                    "gt_data.$": "$.Item.Item.config.M.gt_data.S",
                    "kb_data.$": "$.Item.Item.config.M.kb_data.S",
                    "indexing_algorithm.$": "$.Item.Item.config.M.indexing_algorithm.S",
                    "chunk_overlap.$": "$.Item.Item.config.M.chunk_overlap.N",
                    "retrieval_model.$": "$.Item.Item.config.M.retrieval_model.S",
                    "knn_num.$": "$.Item.Item.config.M.knn_num.N",
                    "chunking_strategy.$": "$.Item.Item.config.M.chunking_strategy.S",
                    "retrieval_service.$": "$.Item.Item.config.M.retrieval_service.S",
                    "embedding_model.$": "$.Item.Item.config.M.embedding_model.S",
                    "embedding_service.$": "$.Item.Item.config.M.embedding_service.S",
                    "n_shot_prompts.$": "$.Item.Item.config.M.n_shot_prompts.N",
                    "chunk_size.$": "$.Item.Item.config.M.chunk_size.N",
                    "vector_dimension.$": "$.Item.Item.config.M.vector_dimension.N",
                    "temp_retrieval_llm.$": "$.Item.Item.config.M.temp_retrieval_llm.N",
                    "aws_region.$": "$.Item.Item.config.M.region.S",
                    "eval_service": "bedrock",
                    "eval_model": "amazon.titan-embed-text-v1",
                    "rerank_model_id.$": "$.Item.Item.config.M.rerank_model_id.S"
                }
            },
            result_path="$.parsedConfig"
        )

        # "Extract config from experiment"
        extract_config_from_experiment_hierarchical = sfn.Pass(
            self,
            "Extract config from experiment for Hierarchical",
            parameters={
                "parsed_config": {
                    "id.$": "$.Item.Item.id.S",
                    "index_id.$": "$.Item.Item.index_id.S",
                    "execution_id.$": "$.Item.Item.execution_id.S",
                    "experiment_id.$": "$.Item.Item.id.S",
                    "gt_data.$": "$.Item.Item.config.M.gt_data.S",
                    "kb_data.$": "$.Item.Item.config.M.kb_data.S",
                    "indexing_algorithm.$": "$.Item.Item.config.M.indexing_algorithm.S",
                    "retrieval_model.$": "$.Item.Item.config.M.retrieval_model.S",
                    "knn_num.$": "$.Item.Item.config.M.knn_num.N",
                    "chunking_strategy.$": "$.Item.Item.config.M.chunking_strategy.S",
                    "retrieval_service.$": "$.Item.Item.config.M.retrieval_service.S",
                    "embedding_model.$": "$.Item.Item.config.M.embedding_model.S",
                    "embedding_service.$": "$.Item.Item.config.M.embedding_service.S",
                    "n_shot_prompts.$": "$.Item.Item.config.M.n_shot_prompts.N",
                    "vector_dimension.$": "$.Item.Item.config.M.vector_dimension.N",
                    "temp_retrieval_llm.$": "$.Item.Item.config.M.temp_retrieval_llm.N",
                    "aws_region.$": "$.Item.Item.config.M.region.S",
                    "eval_service": "bedrock",
                    "eval_model": "amazon.titan-embed-text-v1",
                    "rerank_model_id.$": "$.Item.Item.config.M.rerank_model_id.S",
                    "hierarchical_parent_chunk_size.$": "$.Item.Item.config.M.hierarchical_parent_chunk_size.N",
                    "hierarchical_child_chunk_size.$": "$.Item.Item.config.M.hierarchical_child_chunk_size.N",
                    "hierarchical_chunk_overlap_percentage.$": "$.Item.Item.config.M.hierarchical_chunk_overlap_percentage.N"
                }
            },
            result_path="$.parsedConfig"
        )

        # "Indexing Model Check"
        indexing_model_check = tasks.CallAwsService(
            self,
            "Indexing Model Check",
            service="dynamodb",
            action="getItem",
            parameters={
                "TableName": model_invocations_table_name,
                "Key": {
                    "execution_model_id": {
                        "S.$": "States.Format('{}_{}', $.parsedConfig.parsed_config.embedding_service, $.parsedConfig.parsed_config.embedding_model)"
                    }
                }
            },
            result_path="$.modelInvocations",
            result_selector={
                "invocations.$": "States.MathAdd(States.StringToJson($.Item.invocations.N), 0)",
                "limit.$": "States.MathAdd(States.StringToJson($.Item.limit.N), 0)"
            },
            iam_resources=[vpc_stack.model_invocations_table.table_arn]
        )

        # "Evaluate Indexing Model Check" Choice state
        evaluate_indexing_model_check_choice = sfn.Choice(self, "Evaluate Indexing Model Check")

        # "Wait for Indexing Model Update"
        wait_for_indexing_model_update = sfn.Wait(
            self,
            "Wait for Indexing Model Update",
            time=sfn.WaitTime.duration(Duration.seconds(600))
        )

        # "Indexing Model Invocation Update"
        indexing_model_invocation_update = tasks.CallAwsService(
            self,
            "Indexing Model Invocation Update",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": model_invocations_table_name,
                "Key": {
                    "execution_model_id": {
                        "S.$": "States.Format('{}_{}', $.parsedConfig.parsed_config.embedding_service, $.parsedConfig.parsed_config.embedding_model)"
                    }
                },
                "UpdateExpression": "SET invocations = invocations + :myValueRef",
                "ExpressionAttributeValues": {
                     ":myValueRef": {
                            "N": "1"
                        },
                        ":prevRef": {
                            "N.$": "States.Format('{}', $.modelInvocations.invocations)"
                        },
                        ":limit": {
                            "N.$": "States.Format('{}', $.modelInvocations.limit)"
                        }
                    },
                "ConditionExpression": "invocations = :prevRef AND invocations <> :limit"
            },
            iam_resources=[vpc_stack.model_invocations_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        )

        indexing_model_invocation_update.add_catch(
            indexing_model_check,
            errors=["States.ALL"],
            result_path=sfn.JsonPath.DISCARD
        )

        get_latest_status =  tasks.CallAwsService(
            self,
            "Get latest status",
            service="dynamodb",
            action="getItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                    "id": {
                        "S.$": "$.Item.Item.id.S"
                    }
                }
            },
            result_path="$.modelInvocations",
            iam_resources=[vpc_stack.model_invocations_table.table_arn]
        )

        # "Evaluate Indexing Status" Choice state
        evaluate_indexing_status_choice = sfn.Choice(
            self,
            "Evaluate Indexing Status"
        )

        # "Wait for Indexing Status Update"
        wait_for_indexing_status_update = sfn.Wait(
            self,
            "Wait for Indexing Status Update",
            time=sfn.WaitTime.duration(Duration.seconds(600))
        )

        # "DynamoDB GetItem For Indexing Status"
        dynamodb_get_item_for_indexing_loop = tasks.CallAwsService(
            self,
            "DynamoDB GetItem For Indexing Status Loop",
            service="dynamodb",
            action="getItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                    "id": {
                        "S.$": "$.Item.Item.id.S"
                    }
                }
            },
            result_path="$.Item",
            iam_resources=[vpc_stack.experiment_table.table_arn]
        )

        # "Indexing State Inprogress"
        indexing_state_inprogress_task = tasks.CallAwsService(
            self,
            "Indexing State Inprogress",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                    "id": {
                        "S.$": "$.Item.Item.id.S"
                    }
                },
                "UpdateExpression": "SET index_status = :myValueRef, experiment_status = :expStatusRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "S": "in_progress"
                    },
                    ":expStatusRef": {
                        "S": "indexing_inprogress"
                    }
                }
            },
            iam_resources=[vpc_stack.experiment_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        )

        capture_start_time = tasks.CallAwsService(
            self,
            "CaptureIndexingStartTime",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                    "id": {
                        "S.$": "$.Item.Item.id.S"
                    }
                },
                "UpdateExpression": "SET indexing_start = :startTime",
                "ExpressionAttributeValues": {
                    ":startTime": {
                        "S.$": "$$.State.EnteredTime"
                    }
                }
            },
            iam_resources=[vpc_stack.experiment_table.table_arn],
            result_path="$.indexingStartUpdate"
        )

        # "Run Indexing Task"
        run_indexing_task = tasks.EcsRunTask(
            self,
            "Run Indexing Task",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
            cluster=cluster,
            task_definition=indexing_task_definition,
            launch_target=tasks.EcsFargateLaunchTarget(
                platform_version=ecs.FargatePlatformVersion.LATEST
            ),
            container_overrides=[
                tasks.ContainerOverride(
                    container_definition=indexing_task_definition.default_container,
                    environment=[
                        tasks.TaskEnvironmentVariable(
                            name="EXECUTION_ID",
                            value=sfn.JsonPath.string_at("$.parsedConfig.parsed_config.execution_id")
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="aws_region",
                            value=region
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="experiment_question_metrics_table",
                            value=metrics_table_name
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="execution_table",
                            value=execution_table_name
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="experiment_table",
                            value=experiment_table_name
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="execution_model_invocations_table",
                            value=model_invocations_table_name
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="opensearch_host",
                            value=opensearch_endpoint
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="opensearch_username",
                            value=infraConfig.opensearch_admin_user
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="opensearch_password",
                            value=infraConfig.opensearch_admin_password
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="opensearch_serverless",
                            value="false"
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="inference_system_prompt",
                            value="You are a helpful assistant. Use the provided context to answer questions accurately. If you cannot find the answer in the context, say so"
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="s3_bucket",
                            value=data_bucket_name
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="INPUT_DATA",
                            value=sfn.JsonPath.string_at("States.JsonToString($.parsedConfig.parsed_config)")
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="TASK_TOKEN",
                            value=sfn.JsonPath.task_token
                        )
                    ]
                )
            ],
            assign_public_ip=False,
            security_groups=security_groups,
            subnets=ec2.SubnetSelection(subnets=private_subnets),
            result_path="$.indexTaskStatus"
        )

        # "Evaluate Indexing Task" Choice state
        evaluate_indexing_task_choice = sfn.Choice(self, "Evaluate Indexing Task")

        # "Indexing Model Lock Release on Failure"
        indexing_model_lock_release_on_failure = tasks.CallAwsService(
            self,
            "Indexing Model Lock Release on Failure",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": model_invocations_table_name,
                "Key": {
                    "execution_model_id": {
                        "S.$": "States.Format('{}_{}', $.parsedConfig.parsed_config.embedding_service, $.parsedConfig.parsed_config.embedding_model)"
                    }
                },
                "UpdateExpression": "SET invocations = invocations - :myValueRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "N": "1"
                    }
                }
            },
            iam_resources=[vpc_stack.model_invocations_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        )

        run_indexing_task.add_catch(
            indexing_model_lock_release_on_failure,
            errors=["States.ALL"],
            result_path=sfn.JsonPath.DISCARD
        )

        # "Index Status Failure"
        index_status_failure_task = tasks.CallAwsService(
            self,
            "Index Status Failure",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                        "id": {
                            "S.$": "$.Item.Item.id.S"
                        }
                    },
                "UpdateExpression": "SET index_status = :myValueRef, indexing_end = :timeRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "S": "failed"
                    },
                    ":timeRef": {
                        "S.$": "$$.State.EnteredTime"
                    }
                }
            },
            iam_resources=[vpc_stack.experiment_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        )

        # "Experiment Status Update as Failed"
        experiment_status_update_to_failed = tasks.CallAwsService(
            self,
            "Experiment Status Update as Failed",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                        "id": {
                            "S.$": "$.Item.Item.id.S"
                        }
                    },
                "UpdateExpression": "SET experiment_status = :myValueRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "S": "failed"
                    }
                }
            },
            iam_resources=[vpc_stack.experiment_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        )

        # "Update Experiment End Time"
        update_experiment_end_time = tasks.CallAwsService(
            self,
            "Update experiment end time",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                    "id": {
                        "S.$": "$.Item.Item.id.S"
                    }
                },
                "UpdateExpression": "SET end_datetime = :timeRef",
                "ExpressionAttributeValues": {
                    ":timeRef": {
                        "S.$": "$$.State.EnteredTime"
                    }
                }
            },
            iam_resources=[vpc_stack.experiment_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        ).next(run_cost_lambda_function_task)

        # Create a chain for experiment failure handling
        experiment_failure_chain = experiment_status_update_to_failed.next(update_experiment_end_time)

        # "Index Status Success"
        index_status_success_task = tasks.CallAwsService(
            self,
            "Index Status Success",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                        "id": {
                            "S.$": "$.Item.Item.id.S"
                        }
                    },
                "UpdateExpression": "SET index_status = :myValueRef, experiment_status = :expStatusRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "S": "succeeded"
                    },
                    ":expStatusRef": {
                        "S": "indexing_completed"
                    }
                }
            },
            iam_resources=[vpc_stack.experiment_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        )

        # "Get experiments by index_id"
        get_experiments_by_index_id = tasks.CallAwsService(
            self,
            "Get experiments by index_id",
            service="dynamodb",
            action="query",
            parameters={
                "TableName": experiment_table_name,
                "IndexName": "index_id-index_status-index",
                "KeyConditionExpression": "index_id = :indexId",
                "ExpressionAttributeValues": {
                    ":indexId": {
                        "S.$": "$.Item.Item.index_id.S"
                    }
                }
            },
            result_path="$.toUpdateIds",
            iam_resources=[f"{vpc_stack.experiment_table.table_arn}/index/index_id-index_status-index"]
        )

        # "Update experiment index_status" Map state
        update_experiment_index_status_map = sfn.Map(
            self,
            "Update experiment index_status",
            items_path="$.toUpdateIds.Items",
            result_path=sfn.JsonPath.DISCARD,
            parameters={
                "index_id.$": "$.Item.Item.index_id.S",
                "id.$": "$.Item.Item.id.S"
            }
        )

        dynamodb_update_item = tasks.CallAwsService(
            self,
            "DynamoDB UpdateItem",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                    "id": {
                        "S.$": "$.id"
                    }
                },
                "UpdateExpression": "SET index_status = :indexStatusRef, indexing_end = :endTimeRef",
                "ExpressionAttributeValues": {
                    ":indexStatusRef": {
                        "S": "succeeded"
                    },
                    ":endTimeRef": {
                        "S.$": "$$.State.EnteredTime"
                    }
                }
            },
            iam_resources=[vpc_stack.experiment_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        )

        update_experiment_index_status_map.iterator(dynamodb_update_item)

        # "Index Model Invocation Release"
        indexing_model_invocation_release = tasks.CallAwsService(
            self,
            "Index Model Invocation Release",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": model_invocations_table_name,
                "Key": {
                    "execution_model_id": {
                        "S.$": "States.Format('{}_{}', $.parsedConfig.parsed_config.embedding_service, $.parsedConfig.parsed_config.embedding_model)"
                    }
                },
                "UpdateExpression": "SET invocations = invocations - :myValueRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "N": "1"
                    }
                }
            },
            iam_resources=[vpc_stack.model_invocations_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        )

        # "Proceed to Retrieval Model Check" Pass state
        proceed_to_retrieval_model_check = sfn.Pass(
            self,
            "Proceed to Retrieval Model Check"
        )

        # "Retrieval Model Check"
        retrieval_model_check = tasks.CallAwsService(
            self,
            "Retrieval Model Check",
            service="dynamodb",
            action="getItem",
            parameters={
                "TableName": model_invocations_table_name,
                "Key": {
                    "execution_model_id": {
                        "S.$": "States.Format('{}_{}', $.parsedConfig.parsed_config.retrieval_service, $.parsedConfig.parsed_config.retrieval_model)"
                    }
                }
            },
            result_path="$.retrieval_invocations",
            result_selector={
                "invocations.$": "States.MathAdd(States.StringToJson($.Item.invocations.N), 0)",
                "limit.$": "States.MathAdd(States.StringToJson($.Item.limit.N), 0)"
            },
            iam_resources=[vpc_stack.model_invocations_table.table_arn]
        )

        # "Evaluate Retrieval Model Check" Choice state
        evaluate_retrieval_model_check_choice = sfn.Choice(self, "Evaluate Retrieval Model Check")

        # "Wait for Retrieval Model Update"
        wait_for_retrieval_model_update = sfn.Wait(
            self,
            "Wait for Retrieval Model Update",
            time=sfn.WaitTime.duration(Duration.seconds(600))
        )

        # "Retrieval Model Invocation Update"
        retrieval_model_invocation_update = tasks.CallAwsService(
            self,
            "Retrieval Model Invocation Update",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": model_invocations_table_name,
                "Key": {
                    "execution_model_id": {
                        "S.$": "States.Format('{}_{}', $.parsedConfig.parsed_config.retrieval_service, $.parsedConfig.parsed_config.retrieval_model)"
                    }
                },
                "UpdateExpression": "SET invocations = invocations + :myValueRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                            "N": "1"
                        },
                        ":prevRef": {
                            "N.$": "States.Format('{}', $.retrieval_invocations.invocations)"
                        },
                        ":limit": {
                            "N.$": "States.Format('{}', $.retrieval_invocations.limit)"
                        }
                    },
              "ConditionExpression": "invocations = :prevRef AND invocations <> :limit"
            },
            iam_resources=[vpc_stack.model_invocations_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        )

        retrieval_model_invocation_update.add_catch(
            retrieval_model_check,
            errors=["States.ALL"],
            result_path=sfn.JsonPath.DISCARD
        )

        # "Retrieval State Update"
        retrieval_state_update = tasks.CallAwsService(
            self,
            "Retrieval State Update",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                    "id": {
                        "S.$": "$.Item.Item.id.S"
                    }
                },
                "UpdateExpression": "SET retrieval_status = :myValueRef, experiment_status = :expStatusRef, retrieval_start = :timeStartRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "S": "in_progress"
                    },
                    ":expStatusRef": {
                        "S": "retrieval_inprogress"
                    },
                      ":timeStartRef": {
                        "S.$": "$$.State.EnteredTime"
                    }
                }
            },
            iam_resources=[vpc_stack.experiment_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        )

        # "Run Retrieval Task"
        run_retrieval_task = tasks.EcsRunTask(
            self,
            "Run retrieval task",
            cluster=cluster,
            task_definition=retriever_task_definition,
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
            launch_target=tasks.EcsFargateLaunchTarget(
                platform_version=ecs.FargatePlatformVersion.VERSION1_4
            ),
            container_overrides=[
                tasks.ContainerOverride(
                    container_definition=retriever_task_definition.default_container,
                    environment=[
                        tasks.TaskEnvironmentVariable(
                            name="EXECUTION_ID",
                            value=sfn.JsonPath.string_at("$.parsedConfig.parsed_config.execution_id")
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="aws_region",
                            value=region
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="experiment_question_metrics_table",
                            value=metrics_table_name
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="execution_table",
                            value=execution_table_name
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="experiment_table",
                            value=experiment_table_name
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="execution_model_invocations_table",
                            value=model_invocations_table_name
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="opensearch_host",
                            value=opensearch_endpoint
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="opensearch_username",
                            value=infraConfig.opensearch_admin_user
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="opensearch_password",
                            value=infraConfig.opensearch_admin_password
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="opensearch_serverless",
                            value="false"
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="inference_system_prompt",
                            value="You are a helpful assistant. Use the provided context to answer questions accurately. If you cannot find the answer in the context, say so"
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="s3_bucket",
                            value=data_bucket_name
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="INPUT_DATA",
                            value=sfn.JsonPath.string_at("States.JsonToString($.parsedConfig.parsed_config)")
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="TASK_TOKEN",
                            value=sfn.JsonPath.task_token
                        )
                    ]
                )
            ],
            assign_public_ip=False,
            security_groups=security_groups,
            subnets=ec2.SubnetSelection(subnets=private_subnets),
            result_path="$.retrieverOutput"
        )

        # "Evaluate Retrieval Model Task" Choice state
        evaluate_retrieval_model_task_choice = sfn.Choice(self, "Evaluate Retrieval Model Task")

        # "Retrieval Model Invocation Release"
        retrieval_model_invocation_release = tasks.CallAwsService(
            self,
            "Retrieval Model Invocation Release",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": model_invocations_table_name,
                "Key": {
                    "execution_model_id": {
                        "S.$": "States.Format('{}_{}', $.parsedConfig.parsed_config.retrieval_service, $.parsedConfig.parsed_config.retrieval_model)"
                    }
                },
                "UpdateExpression": "SET invocations = invocations - :val",
                "ExpressionAttributeValues": {
                    ":val": {"N": "1"}
                }
            },
            iam_resources=[vpc_stack.model_invocations_table.table_arn],
            result_path="$.releaseOutput"
        )

        # Define the retrieval_model_check_chain without chaining after Choice state
        retrieval_model_check_chain = retrieval_model_check

        evaluate_retrieval_model_check_choice.when(
            sfn.Condition.number_greater_than_equals_json_path("$.retrieval_invocations.invocations", "$.retrieval_invocations.limit"),
            wait_for_retrieval_model_update.next(retrieval_model_check)
        ).otherwise(
            retrieval_model_invocation_update.next(
                retrieval_state_update.next(
                    run_retrieval_task.next(
                        retrieval_model_invocation_release.next(
                            evaluate_retrieval_model_task_choice
                        )
                    )
                )
            )
        )

        # "Retrieval State Success"
        retrieval_state_success = tasks.CallAwsService(
            self,
            "Retrieval State Success",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                    "id": {"S": sfn.JsonPath.string_at("$.Item.Item.id.S")}
                },
                "UpdateExpression": "SET retrieval_status = :status, experiment_status = :expStatusRef, retrieval_end = :timeEndRef",
                "ExpressionAttributeValues": {
                    ":status": {"S": "success"},
                    ":expStatusRef": {
                        "S": "retrieval_completed"
                    },
                    ":timeEndRef": {
                        "S.$": "$$.State.EnteredTime"
                    }
                }
            },
            iam_resources=[vpc_stack.experiment_table.table_arn],
            result_path="$.retrievalSuccessOutput"
        )

        # "Retrieval State Failure"
        retrieval_state_failure = tasks.CallAwsService(
            self,
            "Retrieval State Failure",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                    "id": {"S": sfn.JsonPath.string_at("$.Item.Item.id.S")}
                },
                "UpdateExpression": "SET retrieval_status = :status, retrieval_end=:timeEndRef",
                "ExpressionAttributeValues": {
                    ":status": {"S": "failed"},
                    ":timeEndRef": {
                        "S.$": "$$.State.EnteredTime"
                    }
                }
            },
            iam_resources=[vpc_stack.experiment_table.table_arn],
            result_path="$.retrievalFailureOutput"
        )

        run_retrieval_task.add_catch(
            retrieval_state_failure,
            errors=["States.ALL"],
            result_path=sfn.JsonPath.DISCARD
        )

        # "Retrieval model lock release on failure"
        retrieval_model_lock_release_on_failure = tasks.CallAwsService(
            self,
            "Retrieval model lock release on failure",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": model_invocations_table_name,
                "Key": {
                    "execution_model_id": {
                        "S.$": "States.Format('{}_{}', $.parsedConfig.parsed_config.retrieval_service, $.parsedConfig.parsed_config.retrieval_model)"
                    }
                },
                "UpdateExpression": "SET invocations = invocations - :myValueRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "N": "1"
                    }
                }
            },
            iam_resources=[vpc_stack.model_invocations_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        ).next(experiment_failure_chain)

        # Adjust retrieval_state_failure to chain correctly
        retrieval_state_failure.next(retrieval_model_lock_release_on_failure)

        # "Eval Model Check"
        eval_model_check = tasks.CallAwsService(
            self,
            "Eval Model Check",
            service="dynamodb",
            action="getItem",
            parameters={
                "TableName": model_invocations_table_name,
                "Key": {
                    "execution_model_id": {
                        "S.$": "States.Format('{}_{}', $.parsedConfig.parsed_config.eval_service, $.parsedConfig.parsed_config.eval_model)"
                    }
                }
            },
            iam_resources=[vpc_stack.model_invocations_table.table_arn],
            result_path="$.eval_invocations",
            result_selector={
                "invocations.$": "States.MathAdd(States.StringToJson($.Item.invocations.N), 0)",
                "limit.$": "States.MathAdd(States.StringToJson($.Item.limit.N), 0)"
            }
        )

        # "Evaluate Retrieval Model Task" Choice logic
        evaluate_retrieval_model_task_choice.when(
            sfn.Condition.string_equals("$.retrieverOutput.status", "success"),
            retrieval_state_success.next(eval_model_check)
        ).when(
            sfn.Condition.string_equals("$.retrieverOutput.status", "failed"),
            retrieval_state_failure
        )

        # "Evaluate eval model check" Choice state
        evaluate_eval_model_check = sfn.Choice(
            self,
            "Evaluate eval model check"
        )

        # "Wait for Eval Model Update"
        wait_for_eval_model_update = sfn.Wait(
            self,
            "Wait for Eval Model Update",
            time=sfn.WaitTime.duration(Duration.seconds(600))
        )

        # "Eval Model Invocation Update"
        eval_model_invocation_update = tasks.CallAwsService(
            self,
            "Eval Model Invocation Update",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": model_invocations_table_name,
                "Key": {
                    "execution_model_id": {
                        "S.$": "States.Format('{}_{}', $.parsedConfig.parsed_config.eval_service, $.parsedConfig.parsed_config.eval_model)"
                    }
                },
                "UpdateExpression": "SET invocations = invocations + :myValueRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "N": "1"
                    },
                    ":prevRef": {
                        "N.$": "States.Format('{}', $.eval_invocations.invocations)"
                    },
                    ":limit": {
                        "N.$": "States.Format('{}', $.eval_invocations.limit)"
                    }
                    
                },
                "ConditionExpression": "invocations = :prevRef AND invocations <> :limit"
            },
            iam_resources=[vpc_stack.model_invocations_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        )

        eval_model_invocation_update.add_catch(
            eval_model_check,
            errors=["States.ALL"],
            result_path=sfn.JsonPath.DISCARD
        )
        # "Update eval status in progress"
        update_eval_status_in_progress = tasks.CallAwsService(
            self,
            "Update eval status in progress",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                    "id": {"S": sfn.JsonPath.string_at("$.Item.Item.id.S")}
                },
                "UpdateExpression": "SET eval_status = :myValueRef, experiment_status = :expStatusRef, eval_start = :timeStartRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "S": "in_progress"
                    },
                    ":expStatusRef": {
                        "S": "eval_inprogress"
                    },
                    ":timeStartRef": {
                        "S.$": "$$.State.EnteredTime"
                    }
                }
            },
            iam_resources=[vpc_stack.experiment_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        )

        # "Run Evaluation Task"
        run_evaluation_task = tasks.EcsRunTask(
            self,
            "Run evaluation task",
            cluster=cluster,
            task_definition=evaluation_task_definition,
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
            launch_target=tasks.EcsFargateLaunchTarget(
                platform_version=ecs.FargatePlatformVersion.VERSION1_4
            ),
            container_overrides=[
                tasks.ContainerOverride(
                    container_definition=evaluation_task_definition.default_container,
                    environment=[
                        tasks.TaskEnvironmentVariable(
                            name="EXECUTION_ID",
                            value=sfn.JsonPath.string_at("$.parsedConfig.parsed_config.execution_id")
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="aws_region",
                            value=region
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="experiment_question_metrics_table",
                            value=metrics_table_name
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="execution_table",
                            value=execution_table_name
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="experiment_table",
                            value=experiment_table_name
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="execution_model_invocations_table",
                            value=model_invocations_table_name
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="opensearch_host",
                            value=opensearch_endpoint
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="opensearch_username",
                            value=infraConfig.opensearch_admin_user
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="opensearch_password",
                            value=infraConfig.opensearch_admin_password
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="opensearch_serverless",
                            value="false"
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="inference_system_prompt",
                            value="You are a helpful assistant. Use the provided context to answer questions accurately. If you cannot find the answer in the context, say so"
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="s3_bucket",
                            value=data_bucket_name
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="INPUT_DATA",
                            value=sfn.JsonPath.string_at("States.JsonToString($.parsedConfig.parsed_config)")
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="TASK_TOKEN",
                            value=sfn.JsonPath.task_token
                        ),
                        tasks.TaskEnvironmentVariable(
                            name="experiment_question_metrics_experimentid_index",
                            value="experiment_id-index"
                        )
                    ]
                )
            ],
            assign_public_ip=False,
            security_groups=security_groups,
            subnets=ec2.SubnetSelection(subnets=private_subnets),
            result_path="$.evaluatorOutput"
        )

        # "Evaluate Task Status" Choice state
        evaluate_task_status_choice = sfn.Choice(self, "Evaluate task status")

        # Connect eval_model_check to evaluate_eval_model_check
        eval_model_check.next(evaluate_eval_model_check)

        # Connect run_evaluation_task to evaluate_task_status_choice
        run_evaluation_task.next(evaluate_task_status_choice)

        # Connect retrieval_model_check to evaluate_retrieval_model_check_choice
        retrieval_model_check.next(evaluate_retrieval_model_check_choice)

        evaluate_eval_model_check.when(
            sfn.Condition.number_greater_than_equals_json_path("$.eval_invocations.invocations", "$.eval_invocations.limit"),
            wait_for_eval_model_update.next(eval_model_check)
        ).otherwise(
            eval_model_invocation_update.next(update_eval_status_in_progress).next(run_evaluation_task)
        )

        # Define the evaluation model check chain without chaining after Choice state
        evaluation_model_check_chain = eval_model_check

        # "Experiment status update to complete"
        experiment_status_update_to_complete = tasks.CallAwsService(
            self,
            "Experiment status update to complete",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                        "id": {
                            "S.$": "$.Item.Item.id.S"
                        }
                    },
                "UpdateExpression": "SET eval_status = :myValueRef, experiment_status = :expStatusRef, eval_end = :timeRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "S": "succeeded"
                    },
                    ":expStatusRef": {
                        "S": "succeeded"
                    },
                     ":timeRef": {
                        "S.$": "$$.State.EnteredTime"
                    }
                }
            },
            iam_resources=[vpc_stack.experiment_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        )

        # "Eval Model Invocation Release"
        eval_model_invocation_release = tasks.CallAwsService(
            self,
            "Eval Model Invocation Release",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": model_invocations_table_name,
                "Key": {
                    "execution_model_id": {
                        "S.$": "States.Format('{}_{}', $.parsedConfig.parsed_config.eval_service, $.parsedConfig.parsed_config.eval_model)"
                    }
                },
                "UpdateExpression": "SET invocations = invocations - :myValueRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "N": "1"
                    }
                }
            },
            iam_resources=[vpc_stack.model_invocations_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        ).next(update_experiment_end_time)

        # "Eval status failed and experiment complete"
        eval_status_failed_and_experiment_complete = tasks.CallAwsService(
            self,
            "Eval status failed and experiment complete",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": experiment_table_name,
                "Key": {
                    "id": {
                        "S.$": "$.Item.Item.id.S"
                    }
                },
                "UpdateExpression": "SET eval_status = :myValueRef, experiment_status = :expStatusRef, eval_end = :timeRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "S": "failed"
                    },
                    ":expStatusRef": {
                        "S": "failed"
                    },
                    ":timeRef": {
                        "S.$": "$$.State.EnteredTime"
                    }
                }
            },
            iam_resources=[vpc_stack.experiment_table.table_arn],
            result_path=sfn.JsonPath.DISCARD
        ).next(update_experiment_end_time)

        run_evaluation_task.add_catch(
            eval_status_failed_and_experiment_complete,
            errors=["States.ALL"],
            result_path=sfn.JsonPath.DISCARD
        )

        # "Evaluate Task Status" Choice logic
        evaluate_task_status_choice.when(
            sfn.Condition.string_equals("$.evaluatorOutput.status", "success"),
            experiment_status_update_to_complete.next(eval_model_invocation_release)
        ).when(
            sfn.Condition.string_equals("$.evaluatorOutput.status", "failed"),
            eval_status_failed_and_experiment_complete
        )

        # Build the evaluation chain
        # Adjust the chain inside the Experiments Map iterator
        experiments_map_definition = update_experiment_start_time\
            .next(dynamodb_get_item_by_id)\
            .next(evaluate_chunking_strategy_choice)

        indexing_model_check.next(evaluate_indexing_model_check_choice)

        # Set up the choices for "Evaluate Chunking Strategy"
        evaluate_chunking_strategy_choice.when(
            sfn.Condition.string_equals("$.Item.Item.config.M.chunking_strategy.S", "hierarchical"),
            extract_config_from_experiment_hierarchical.next(indexing_model_check)
        ).otherwise(
            extract_config_from_experiment.next(indexing_model_check)
        )


        # Set up the choices for "Evaluate Indexing Model Check"
        evaluate_indexing_model_check_choice.when(
            sfn.Condition.number_greater_than_equals_json_path("$.modelInvocations.invocations", "$.modelInvocations.limit"),
            wait_for_indexing_model_update.next(indexing_model_check)
        ).otherwise(
            indexing_model_invocation_update.next(get_latest_status)
        )

        get_latest_status.next(evaluate_indexing_status_choice)

        indexing_model_invocation_release_chain = indexing_model_invocation_release.next(proceed_to_retrieval_model_check)

        # Set up the choices for "Evaluate Indexing Status"
        evaluate_indexing_status_choice.when(
            sfn.Condition.string_equals("$.Item.Item.index_status.S", "not_started"),
            capture_start_time.next(indexing_state_inprogress_task).next(run_indexing_task).next(evaluate_indexing_task_choice)
        ).when(
            sfn.Condition.string_equals("$.Item.Item.index_status.S", "in_progress"),
            wait_for_indexing_status_update.next(dynamodb_get_item_for_indexing_loop).next(evaluate_indexing_status_choice)
        ).when(
            sfn.Condition.string_equals("$.Item.Item.index_status.S", "succeeded"),
            indexing_model_invocation_release_chain
        ).when(
            sfn.Condition.string_equals("$.Item.Item.index_status.S", "failed"),
            experiment_failure_chain
        ).otherwise(
            experiment_failure_chain
        )

        index_status_failure_task_chain = index_status_failure_task.next(experiment_failure_chain)

        # Set up the choices for "Evaluate Indexing Task"
        evaluate_indexing_task_choice.when(
            sfn.Condition.string_equals("$.indexTaskStatus.status", "success"),
            index_status_success_task.next(get_experiments_by_index_id).next(update_experiment_index_status_map).next(indexing_model_invocation_release_chain)
        ).when(
            sfn.Condition.string_equals("$.indexTaskStatus.status", "failed"),
            indexing_model_lock_release_on_failure.next(index_status_failure_task_chain)
        ).otherwise(
            index_status_failure_task_chain
        )

        # Attach the retrieval_model_check_chain to proceed_to_retrieval_model_check
        proceed_to_retrieval_model_check.next(retrieval_model_check)

        # Create a final execution status update task
        final_execution_status_task = tasks.CallAwsService(
            self,
            "Final Update Execution status",
            service="dynamodb",
            action="updateItem",
            parameters={
                "TableName": execution_table_name,
                "Key": {
                    "id": {
                        "S.$": "$.Items[0].execution_id.S"
                    }
                },
                "UpdateExpression": "SET #val = :myValueRef",
                "ExpressionAttributeValues": {
                    ":myValueRef": {
                        "S": "completed"
                    }
                },
                "ExpressionAttributeNames": {
                    "#val": "status"
                }
            },
            iam_resources=[vpc_stack.execution_table.table_arn],
            result_path=sfn.JsonPath.DISCARD,
            output_path=sfn.JsonPath.DISCARD,
            comment="Update Execution status to completed"
        )

        create_opensearch_indices_task.add_catch(
            final_execution_status_task,
            errors=["States.ALL"]
        )

        # Build the state machine definition
        definition = sfn.Chain.start(inject_config)\
            .next(query_model_invocations_task)\
            .next(clear_invocations_map)\
            .next(wait_for_model_invocations_cleared)\
            .next(query_task)\
            .next(create_opensearch_indices_task)\
            .next(index_creation_evaluation_choice)

        # Set up the choices in "Index creation evaluation"
        index_creation_evaluation_choice.when(
            sfn.Condition.string_equals("$.indexCreation.Payload.status", "success"),
            experiments_map.next(final_execution_status_task)
        ).otherwise(
            final_execution_status_task
        )

        # Attach the experiments_map to the definition
        experiments_map.iterator(experiments_map_definition)

        # Create the state machine
        state_machine = sfn.StateMachine(
            self,
            "FlotorchStateMachine",
            state_machine_name=state_machine_name,
            definition=definition,
            role=state_machine_role,
            timeout=Duration.hours(24),
            logs=sfn.LogOptions(
                destination=logs.LogGroup(
                    self,
                    "StateMachineLogGroup",
                    log_group_name=f"/aws/vendedlogs/states/{state_machine_name}",
                    removal_policy=RemovalPolicy.DESTROY
                ),
                level=sfn.LogLevel.ALL
            )
        )

        CfnOutput(
            self,
            "StateMachineArn",
            value=state_machine.state_machine_arn,
            description="Step Functions State Machine ARN"
        )