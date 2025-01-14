from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_dynamodb as dynamodb,
    aws_opensearchservice as opensearch,
    aws_ecr as ecr,
    aws_s3 as s3,
    aws_iam as iam,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
    aws_ecs as ecs,
    aws_apprunner as apprunner,
    aws_lambda as lambda_,
    CfnOutput,
    RemovalPolicy,
    SecretValue,
    Aws,
    Duration,
    CustomResource,
    custom_resources as cr
)
from aws_cdk.aws_stepfunctions import DefinitionBody
from constructs import Construct
import random
import string
import json
from vpc.config import InfraConfig

class VPCStack(Stack):
    def __init__(self, scope: Construct, id: str, table_suffix: str, existing_bucket_name: str = None, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Generate random 6-character suffix
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

        # Ensure the stack is environment-specific
        if not self.account or not self.region:
            raise ValueError("Stack must be environment-specific (account and region must be specified)")

        # IAM Role with Full Access to S3, DynamoDB, Bedrock, Sagemaker, OpenSearchService, Opensearch Ingestion, AppRunner, ECR, ECS, VPC and EC2
        self.role = iam.Role(
            self,
            f"FlotorchRole-{table_suffix}",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("ec2.amazonaws.com"),
                iam.ServicePrincipal("sagemaker.amazonaws.com"),
                iam.ServicePrincipal("bedrock.amazonaws.com")
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonOpenSearchServiceFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryFullAccess")
            ]
        )

        # Getting values from config
        infraConfig = InfraConfig()

        # Create VPC
        self.vpc = ec2.Vpc(
            self,
            f"FlotorchVPC-{table_suffix}",
            max_azs=3,
            ip_addresses=ec2.IpAddresses.cidr(infraConfig.vpc_cidr),
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        )

        # S3 Bucket
        bucket_name = existing_bucket_name or f"flotorch-data-{self.account}-{self.region}-{table_suffix}"
        if existing_bucket_name:
            self.data_bucket = s3.Bucket.from_bucket_name(
                self,
                f"FlotorchDataBucket-{table_suffix}",
                existing_bucket_name
            )
        else:
            self.data_bucket = s3.Bucket(
                self,
                f"FlotorchDataBucket-{table_suffix}",
                bucket_name=bucket_name,
                encryption=s3.BucketEncryption.S3_MANAGED,
                block_public_access=s3.BlockPublicAccess(
                    block_public_acls=False,
                    block_public_policy=False,
                    ignore_public_acls=False,
                    restrict_public_buckets=False
                ),
                removal_policy=RemovalPolicy.DESTROY,
                auto_delete_objects=True,
                versioned=True,
                cors=[s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT, s3.HttpMethods.POST, s3.HttpMethods.DELETE, s3.HttpMethods.HEAD],
                    allowed_origins=['*'],
                    allowed_headers=['*'],
                    max_age=3000
                )]
            )

        # Execution Table
        self.execution_table = dynamodb.Table(
            self,
            f"Execution-{table_suffix}",
            table_name=f"Execution_{table_suffix}",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        # Add GSIs for Execution table with attribute definitions
        execution_gsi_fields = {
            "id": dynamodb.AttributeType.STRING,
            "created_date": dynamodb.AttributeType.STRING,
            "config": dynamodb.AttributeType.STRING,
            "status": dynamodb.AttributeType.STRING,
            "gt_data": dynamodb.AttributeType.STRING,
            "kb_data": dynamodb.AttributeType.STRING,
            "region": dynamodb.AttributeType.STRING
        }

        self.execution_table.add_global_secondary_index(
            index_name="status-index",
            partition_key=dynamodb.Attribute(
                name="status",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        self.experiment_table = dynamodb.Table(
            self,
            f"Experiment-{table_suffix}",
            table_name=f"Experiment_{table_suffix}",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        # Add GSIs for Experiment table with attribute definitions
        experiment_gsi_fields = {
            "id": dynamodb.AttributeType.STRING,
            "execution_id": dynamodb.AttributeType.STRING,
            "start_datetime": dynamodb.AttributeType.STRING,
            "end_datetime": dynamodb.AttributeType.STRING,
            "config": dynamodb.AttributeType.STRING,
            "experiment_status": dynamodb.AttributeType.STRING,
            "index_status": dynamodb.AttributeType.STRING,
            "retrieval_status": dynamodb.AttributeType.STRING,
            "eval_status": dynamodb.AttributeType.STRING,
            "index_id": dynamodb.AttributeType.STRING,
            "indexing_time": dynamodb.AttributeType.NUMBER,
            "retrieval_time": dynamodb.AttributeType.NUMBER,
            "total_time": dynamodb.AttributeType.NUMBER,
            "cost": dynamodb.AttributeType.NUMBER,
            "eval_metrics": dynamodb.AttributeType.STRING
        }

        self.experiment_table.add_global_secondary_index(
            index_name="index_id-index_status-index",
            partition_key=dynamodb.Attribute(
                name="index_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="index_status",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        self.experiment_table.add_global_secondary_index(
            index_name="execution_id-index",
            partition_key=dynamodb.Attribute(
                name="execution_id",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        self.metrics_table = dynamodb.Table(
            self,
            f"ExperimentQuestionMetrics-{table_suffix}",
            table_name=f"ExperimentQuestionMetrics_{table_suffix}",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        # Add GSIs for Metrics table with attribute definitions
        metrics_gsi_fields = {
            "id": dynamodb.AttributeType.STRING,
            "execution_id": dynamodb.AttributeType.STRING,
            "experiment_id": dynamodb.AttributeType.STRING,
            "question": dynamodb.AttributeType.STRING,
            "gt_answer": dynamodb.AttributeType.STRING,
            "generated_answer": dynamodb.AttributeType.STRING,
            "created_date": dynamodb.AttributeType.STRING,
            "eval_metrics": dynamodb.AttributeType.STRING
        }

        # Add Global Secondary Indexes for the Metrics table
        self.metrics_table.add_global_secondary_index(
            index_name="execution_id-experiment_id-index",
            partition_key=dynamodb.Attribute(
                name="execution_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="experiment_id",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        self.metrics_table.add_global_secondary_index(
            index_name="experiment_id-index",
            partition_key=dynamodb.Attribute(
                name="experiment_id",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # Model Invocations Table
        self.model_invocations_table = dynamodb.Table(
            self,
            f"ExecutionModelInvocations-{table_suffix}",
            table_name=f"ExecutionModelInvocations_{table_suffix}",
            partition_key=dynamodb.Attribute(
                name="execution_model_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        # Add GSIs for Model Invocations table with attribute definitions
        model_invocations_gsi_fields = {
            "execution_model_id": dynamodb.AttributeType.STRING,
            "invocations": dynamodb.AttributeType.NUMBER,
            "version": dynamodb.AttributeType.NUMBER
        }

        # Create OpenSearch Security Group
        self.opensearch_sg = ec2.SecurityGroup(
            self,
            f"OpenSearchSecurityGroup-{table_suffix}",
            vpc=self.vpc,
            description="Security group for OpenSearch domain",
            security_group_name=f"OpenSearchSecurityGroup-{table_suffix}",
            allow_all_outbound=True
        )

        # Create Lambda Security Group
        self.lambda_sg = ec2.SecurityGroup(
            self,
            f"LambdaSecurityGroup-{table_suffix}",
            vpc=self.vpc,
            allow_all_outbound=True,
            description='Security group for Lambda functions',
            security_group_name=f"LambdaSecurityGroup-{table_suffix}"
        )

        # Allow access from VPC subnets to OpenSearch domain
        self.opensearch_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS access from VPC"
        )

        # Allow Lambda to access OpenSearch
        self.opensearch_sg.add_ingress_rule(
            peer=self.lambda_sg,
            connection=ec2.Port.tcp(443),
            description='Allow Lambda to access OpenSearch'
        )

        # Create OpenSearch Domain
        es_password = infraConfig.opensearch_admin_password
        master_user_password = SecretValue.unsafe_plain_text(es_password)

        self.opensearch_domain = opensearch.Domain(
            self,
            "FlotorchOpenSearch",
            version=opensearch.EngineVersion.OPENSEARCH_2_17,
            domain_name=f"flotorch-{table_suffix}",
            vpc=self.vpc,
            vpc_subnets=[ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                availability_zones=[self.vpc.availability_zones[0]]
            )],
            security_groups=[self.opensearch_sg],
            capacity=opensearch.CapacityConfig(
                data_node_instance_type="r7g.2xlarge.search",
                data_nodes=3
            ),
            ebs=opensearch.EbsOptions(
                volume_size=500,  # 500 GB
                volume_type=ec2.EbsDeviceVolumeType.GP3,
                iops=16000,  # 16000 IOPS
                throughput=1000  # 1000 MiB/s
            ),
            fine_grained_access_control=opensearch.AdvancedSecurityOptions(
                master_user_name=infraConfig.opensearch_admin_user,
                master_user_password=master_user_password
            ),
            enforce_https=True,
            node_to_node_encryption=True,
            encryption_at_rest=opensearch.EncryptionAtRestOptions(
                enabled=True
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        # Add access policy to the OpenSearch domain
        access_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            principals=[iam.AnyPrincipal()],
            actions=["es:*"],
            resources=[f"{self.opensearch_domain.domain_arn}/*"]
        )
        self.opensearch_domain.add_access_policies(access_policy)

        # Create ECR Repositories
        self.ecr_repos = {}
        for repo_name in ["indexing", "retriever", "app", "evaluation", "runtime"]:
            self.ecr_repos[repo_name] = ecr.Repository(
                self,
                f"{repo_name.capitalize()}Repository",
                repository_name=f"flotorch-{repo_name}-{table_suffix}",
                removal_policy=RemovalPolicy.DESTROY
            )
                      
        # Create ECS Cluster
        self.ecs_cluster = ecs.Cluster(
            self,
            f"FlotorchCluster-{table_suffix}",
            vpc=self.vpc
        )

        # Create Task Role
        task_role = iam.Role(
            self,
            f"FlotorchTaskRole-{table_suffix}",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        # Add required permissions to task role
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
        )
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AWSStepFunctionsFullAccess")
        )
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess")
        )
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonOpenSearchServiceFullAccess")
        )
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonOpenSearchIngestionFullAccess")
        )
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
        )
        task_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:*",
                    "states:StartExecution",
                    "states:StopExecution",
                    "states:DescribeExecution",
                    "states:ListExecutions",
                    "states:SendTaskFailure",
                    "states:SendTaskHeartbeat",
                    "states:SendTaskSuccess",
                    "es:*"
                ],
                resources=[
                    self.execution_table.table_arn,
                    self.experiment_table.table_arn,
                    self.metrics_table.table_arn,
                    self.model_invocations_table.table_arn,
                    f"arn:aws:states:{self.region}:{self.account}:stateMachine:*",
                    f"arn:aws:states:{self.region}:{self.account}:execution:*:*",
                    f"arn:aws:es:{self.region}:{self.account}:domain/*"
                ]
            )
        )

        # Create Task Definition for each service
        self.task_definitions = {}
        for service in ["indexing", "retriever", "evaluation"]:
            self.task_definitions[service] = ecs.FargateTaskDefinition(
                self,
                f"FlotorchTask{service.capitalize()}-{table_suffix}",
                memory_limit_mib=4096,
                cpu=2048,
                task_role=task_role
            )

            # Add container to task definition
            self.task_definitions[service].add_container(
                f"FlotorchContainer{service.capitalize()}-{table_suffix}",
                image=ecs.ContainerImage.from_ecr_repository(
                    self.ecr_repos[service]
                ),
                logging=ecs.LogDriver.aws_logs(
                    stream_prefix=f"flotorch-{service}"
                ),
                environment={
                    "AWS_REGION": self.region,
                    "DATA_BUCKET": self.data_bucket.bucket_name,
                    "EXECUTION_TABLE": self.execution_table.table_name,
                    "EXPERIMENT_TABLE": self.experiment_table.table_name,
                    "METRICS_TABLE": self.metrics_table.table_name,
                    "MODEL_INVOCATIONS_TABLE": self.model_invocations_table.table_name,
                    "OPENSEARCH_HOST": self.opensearch_domain.domain_endpoint,
                    "OPENSEARCH_USERNAME": infraConfig.opensearch_admin_user,
                    "OPENSEARCH_PASSWORD": infraConfig.opensearch_admin_password
                }
            )

        # Create Step Functions Role with required permissions
        step_functions_role = iam.Role(
            self,
            f"StepFunctionRole-{table_suffix}",
            assumed_by=iam.ServicePrincipal("states.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSStepFunctionsFullAccess")
            ]
        )

        # Add ECS permissions
        step_functions_role.add_to_policy(
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

        # Add CloudWatch Logs permissions
        step_functions_role.add_to_policy(
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

        # Add IAM permissions for task roles
        step_functions_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "iam:GetRole",
                    "iam:PassRole"
                ],
                resources=[
                    task_role.role_arn,
                    self.task_definitions["indexing"].execution_role.role_arn,
                    self.task_definitions["retriever"].execution_role.role_arn,
                    self.task_definitions["evaluation"].execution_role.role_arn
                ]
            )
        )

        # Add DynamoDB permissions
        step_functions_role.add_to_policy(
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
                    self.experiment_table.table_arn,
                    self.execution_table.table_arn,
                    self.model_invocations_table.table_arn,
                    self.metrics_table.table_arn,
                    f"{self.experiment_table.table_arn}/index/*",
                    f"{self.execution_table.table_arn}/index/*",
                    f"{self.model_invocations_table.table_arn}/index/*",
                    f"{self.metrics_table.table_arn}/index/*"
                ]
            )
        )

        # Add Lambda invocation permission
        step_functions_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "lambda:InvokeFunction"
                ],
                resources=["*"]
            )
        )

        # Add BedRock permissions
        step_functions_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedRockFullAccess")
        )

        # Add SageMaker permissions
        step_functions_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
        )

        # Add SageMaker Canvas permissions
        step_functions_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerCanvasFullAccess")
        )

        # Add S3 Full Access
        step_functions_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )

        # Create network configuration for ECS tasks
        vpc_subnets = ec2.SubnetSelection(
            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
        )

        # Create Security Groups
        self.indexer_security_group = ec2.SecurityGroup(
            self,
            f"IndexerSecurityGroup-{table_suffix}",
            vpc=self.vpc,
            allow_all_outbound=True
        )

        self.retriever_security_group = ec2.SecurityGroup(
            self,
            f"RetrieverSecurityGrou-{table_suffix}",
            vpc=self.vpc,
            allow_all_outbound=True
        )

        self.evaluation_security_group = ec2.SecurityGroup(
            self,
            f"EvaluationSecurityGroup-{table_suffix}",
            vpc=self.vpc,
            allow_all_outbound=True
        )

        # Create Step Functions tasks
        run_indexer = sfn_tasks.EcsRunTask(
            self,
            f"Run Indexer - {table_suffix}",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
            cluster=self.ecs_cluster,
            task_definition=self.task_definitions["indexing"],
            launch_target=sfn_tasks.EcsFargateLaunchTarget(
                platform_version=ecs.FargatePlatformVersion.LATEST
            ),
            container_overrides=[
                sfn_tasks.ContainerOverride(
                    container_definition=self.task_definitions["indexing"].default_container,
                    environment=[
                        sfn_tasks.TaskEnvironmentVariable(
                            name="EXECUTION_ID",
                            value=sfn.JsonPath.string_at("$.execution_id")
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="vector_field_name",
                            value="vectors"
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="opensearch_serverless",
                            value="false"
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="aws_region",
                            value=self.region
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="experiment_question_metrics_table",
                            value=self.metrics_table.table_name
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="execution_table",
                            value=self.execution_table.table_name
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="experiment_table",
                            value=self.experiment_table.table_name
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="execution_model_invocations_table",
                            value=self.model_invocations_table.table_name
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="opensearch_host",
                            value=self.opensearch_domain.domain_endpoint
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="opensearch_username",
                            value=infraConfig.opensearch_admin_user
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="opensearch_password",
                            value=infraConfig.opensearch_admin_password
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="inference_system_prompt",
                            value="You are a helpful assistant. Use the provided context to answer questions accurately. If you cannot find the answer in the context, say so"
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="s3_bucket",
                            value=self.data_bucket.bucket_name
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="INPUT_DATA",
                            value="States.JsonToString($.parsedConfig.parsed_config)"
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="TASK_TOKEN",
                            value="$$.Task.Token"
                        )
                    ]
                )
            ],
            subnets=vpc_subnets,
            security_groups=[self.indexer_security_group],
            assign_public_ip=False
        )

        run_retriever = sfn_tasks.EcsRunTask(
            self,
            f"Run Retriever - {table_suffix}",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
            cluster=self.ecs_cluster,
            task_definition=self.task_definitions["retriever"],
            launch_target=sfn_tasks.EcsFargateLaunchTarget(
                platform_version=ecs.FargatePlatformVersion.LATEST
            ),
            container_overrides=[
                sfn_tasks.ContainerOverride(
                    container_definition=self.task_definitions["retriever"].default_container,
                    environment=[
                        sfn_tasks.TaskEnvironmentVariable(
                            name="EXECUTION_ID",
                            value=sfn.JsonPath.string_at("$.execution_id")
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="aws_region",
                            value=self.region
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="experiment_question_metrics_table",
                            value=self.metrics_table.table_name
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="execution_table",
                            value=self.execution_table.table_name
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="experiment_table",
                            value=self.experiment_table.table_name
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="execution_model_invocations_table",
                            value=self.model_invocations_table.table_name
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="opensearch_host",
                            value=self.opensearch_domain.domain_endpoint
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="opensearch_username",
                            value=infraConfig.opensearch_admin_user
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="opensearch_password",
                            value=infraConfig.opensearch_admin_password
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="inference_system_prompt",
                            value="You are a helpful assistant. Use the provided context to answer questions accurately. If you cannot find the answer in the context, say so"
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="s3_bucket",
                            value=self.data_bucket.bucket_name
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="INPUT_DATA",
                            value="States.JsonToString($.parsedConfig.parsed_config)"
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="TASK_TOKEN",
                            value="$$.Task.Token"
                        )
                    ]
                )
            ],
            subnets=vpc_subnets,
            security_groups=[self.retriever_security_group],
            assign_public_ip=False
        )

        run_evaluation = sfn_tasks.EcsRunTask(
            self,
            f"Run Evaluation - {table_suffix}",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
            cluster=self.ecs_cluster,
            task_definition=self.task_definitions["evaluation"],
            launch_target=sfn_tasks.EcsFargateLaunchTarget(
                platform_version=ecs.FargatePlatformVersion.LATEST
            ),
            container_overrides=[
                sfn_tasks.ContainerOverride(
                    container_definition=self.task_definitions["evaluation"].default_container,
                    environment=[
                        sfn_tasks.TaskEnvironmentVariable(
                            name="EXECUTION_ID",
                            value=sfn.JsonPath.string_at("$.execution_id")
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="aws_region",
                            value=self.region
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="experiment_question_metrics_table",
                            value=self.metrics_table.table_name
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="execution_table",
                            value=self.execution_table.table_name
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="experiment_table",
                            value=self.experiment_table.table_name
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="execution_model_invocations_table",
                            value=self.model_invocations_table.table_name
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="opensearch_host",
                            value=self.opensearch_domain.domain_endpoint
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="opensearch_username",
                            value=infraConfig.opensearch_admin_user
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="opensearch_password",
                            value=infraConfig.opensearch_admin_password
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="inference_system_prompt",
                            value="You are a helpful assistant. Use the provided context to answer questions accurately. If you cannot find the answer in the context, say so"
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="s3_bucket",
                            value=self.data_bucket.bucket_name
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="INPUT_DATA",
                            value="States.JsonToString($.parsedConfig.parsed_config)"
                        ),
                        sfn_tasks.TaskEnvironmentVariable(
                            name="TASK_TOKEN",
                            value="$$.Task.Token"
                        )
                    ]
                )
            ],
            subnets=vpc_subnets,
            security_groups=[self.evaluation_security_group],
            assign_public_ip=False
        )

        # Create Step Functions definition
        definition = run_indexer.next(run_retriever).next(run_evaluation)

        # Create Step Functions state machine for ECS
        self.state_machine_ecs = sfn.StateMachine(
            self,
            f"FlotorchStateMachine-ECS-{table_suffix}",
            role=step_functions_role,
            definition=definition
        )

        # Create VPC Connector for App Runner
        self.vpc_connector = apprunner.CfnVpcConnector(
            self,
            f"AppRunnerVpcConnector-{table_suffix}",
            vpc_connector_name=f"flotorch-vpc-connector-{table_suffix}",
            subnets=self.vpc.select_subnets(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ).subnet_ids,
            security_groups=[
                self.vpc.vpc_default_security_group
            ]
        )

        # Create Lambda layer for pandas
        pandas_layer = lambda_.LayerVersion.from_layer_version_arn(
            self,
            f"AWSSDKPandasLayer-{table_suffix}",
            "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python39:28"
        )

        # Create Cost Lambda function
        cost_lambda_function = lambda_.Function(
            self,
            f"FlotorchCostComputeLambda-{table_suffix}",
            function_name=f"FlotorchCostComputeLambda-{table_suffix}",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("../lambda_handlers/cost_handler"),
            handler="cost_compute_handler.lambda_handler",
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[self.lambda_sg],
            timeout=Duration.seconds(300),
            memory_size=1024,
            layers=[pandas_layer],
            environment={
                "execution_table": self.execution_table.table_name,
                "experiment_table": self.experiment_table.table_name,
                "aws_region": self.region,
                "s3_bucket": self.data_bucket.bucket_name,
                "bedrock_limit_csv": "seed/bedrock_limits_small.csv"
            }
        )

        # Grant DynamoDB read/write permissions to the Lambda function
        self.execution_table.grant_read_write_data(cost_lambda_function)
        self.experiment_table.grant_read_write_data(cost_lambda_function)

        # Grant S3 read permissions to the Lambda function
        self.data_bucket.grant_read(cost_lambda_function)

        # Outputs
        CfnOutput(self, "VPCId", value=self.vpc.vpc_id)
        CfnOutput(self, "OpenSearchDomainEndpoint", value=self.opensearch_domain.domain_endpoint)
        CfnOutput(self, "DataBucketName", value=self.data_bucket.bucket_name)
        CfnOutput(
            self,
            "ECSClusterArn",
            value=self.ecs_cluster.cluster_arn,
            description="ECS Cluster ARN"
        )
        CfnOutput(
            self,
            "ECSStateMachineArn",
            value=self.state_machine_ecs.state_machine_arn,
            description=f"ECS Step Functions State Machine ARN for {table_suffix}"
        )
        CfnOutput(
            self,
            "FlotorchRoleArn",
            value=self.role.role_arn,
            description="ARN of the Flotorch IAM Role"
        )
        CfnOutput(self, "ExecutionTableName", value=self.execution_table.table_name)
        CfnOutput(self, "ExperimentTableName", value=self.experiment_table.table_name)
        CfnOutput(self, "MetricsTableName", value=self.metrics_table.table_name)
        CfnOutput(self, "ModelInvocationsTableName", value=self.model_invocations_table.table_name)
