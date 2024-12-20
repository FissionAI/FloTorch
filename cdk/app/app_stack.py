from aws_cdk import (
    Stack,
    aws_apprunner as apprunner,
    aws_iam as iam,
    aws_ecr as ecr,
    aws_lambda as lambda_,
    Duration,
    aws_ec2 as ec2,
    CfnOutput
)
from constructs import Construct
from vpc.config import InfraConfig

class AppStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc_stack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        infraConfig = InfraConfig()

        table_suffix = id.split('-')[-1]

        # Create App Runner Instance Role
        instance_role = iam.Role(
            self,
            f"AppRunnerInstanceRole-{table_suffix}",
            assumed_by=iam.ServicePrincipal("tasks.apprunner.amazonaws.com")
        )

        # Add S3 access to the specific data bucket
        instance_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:*"],
            resources=[f"{vpc_stack.data_bucket.bucket_arn}/*", f"{vpc_stack.data_bucket.bucket_arn}/"]
        ))

        # Add Step Functions full access
        instance_role.add_to_policy(iam.PolicyStatement(
            actions=["states:*"],
            resources=[f"arn:aws:states:{self.region}:{self.account}:stateMachine:FlotorchStateMachine-{table_suffix}"]
        ))

        # Add DynamoDB access to specific tables
        instance_role.add_to_policy(iam.PolicyStatement(
            actions=["dynamodb:*"],
            resources=[
                vpc_stack.execution_table.table_arn,
                vpc_stack.experiment_table.table_arn,
                vpc_stack.metrics_table.table_arn,
                vpc_stack.model_invocations_table.table_arn,
                f"{vpc_stack.execution_table.table_arn}/index/*",
                f"{vpc_stack.experiment_table.table_arn}/index/*",
                f"{vpc_stack.metrics_table.table_arn}/index/*",
                f"{vpc_stack.model_invocations_table.table_arn}/index/*"
            ]
        ))


        # Create App Runner Access Role for ECR
        access_role = iam.Role(
            self,
            f"AppRunnerAccessRole-{table_suffix}",
            assumed_by=iam.ServicePrincipal("build.apprunner.amazonaws.com"),
            inline_policies={
                "ECRAccess": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "ecr:GetAuthorizationToken",
                                "ecr:BatchCheckLayerAvailability",
                                "ecr:GetDownloadUrlForLayer",
                                "ecr:BatchGetImage"
                            ],
                            resources=["*"]
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "ecr:DescribeImages",
                                "ecr:ListImages"
                            ],
                            resources=[vpc_stack.ecr_repos["app"].repository_arn]
                        )
                    ]
                )
            }
        )

        # Get nginx auth credentials from context
        nginx_user = self.node.try_get_context('NGINX_AUTH_USER') or 'admin'
        nginx_password = self.node.try_get_context('NGINX_AUTH_PASSWORD')

        # Create environment variables for App Runner
        env_vars = [
            apprunner.CfnService.KeyValuePairProperty(
                name="AWS_DEFAULT_REGION",
                value=self.region
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="AWS_REGION",
                value=self.region
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="OPENSEARCH_ENDPOINT",
                value=vpc_stack.opensearch_domain.domain_endpoint
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="DATA_BUCKET",
                value=vpc_stack.data_bucket.bucket_name
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="ECS_STEP_FUNCTION_ARN",
                value=vpc_stack.state_machine_ecs.state_machine_arn
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="PORT",
                value="80"
            ),
             apprunner.CfnService.KeyValuePairProperty(
                name="aws_region",
                value=self.region
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="experiment_question_metrics_table",
                value=f"ExperimentQuestionMetrics_{table_suffix}"
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="execution_table",
                value=f"Execution_{table_suffix}"
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="experiment_table",
                value=f"Experiment_{table_suffix}"
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="execution_model_invocations_table",
                value=f"ExecutionModelInvocations_{table_suffix}"
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="step_function_arn",
                value=f"arn:aws:states:{self.region}:{self.account}:stateMachine:FlotorchStateMachine-{table_suffix}"
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="opensearch_host",
                value=vpc_stack.opensearch_domain.domain_endpoint
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="opensearch_username",
                value=infraConfig.opensearch_admin_user
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="opensearch_password",
                value=infraConfig.opensearch_admin_password
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="opensearch_serverless",
                value="false"
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="vector_field_name",
                value="vectors"
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="bedrock_role_arn",
                value=vpc_stack.role.role_arn
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="sagemaker_role_arn",
                value=vpc_stack.role.role_arn
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="inference_system_prompt",
                value="You are an intelligent assistant. Answer user questions using only the provided context. Do not make up information, make assumptions or use external knowledge. If the context does not contain the answer, explicitly state that. Do not disclose sensitive information. Maintain a professional tone and ensure responses are accurate and relevant without assumptions."
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="s3_bucket",
                value=vpc_stack.data_bucket.bucket_name
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="bedrock_limit_csv",
                value="seed/bedrock_limits_small.csv"
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="NGINX_AUTH_USER",
                value=nginx_user
            ),
            apprunner.CfnService.KeyValuePairProperty(
                name="NGINX_AUTH_PASSWORD",
                value=nginx_password
            )
        ]

        # Create App Runner Service
        webapp_service = apprunner.CfnService(
            self,
            f"FlotorchWebApp-{table_suffix}",
            service_name=f"flotorch-webapp-{table_suffix}",
            source_configuration=apprunner.CfnService.SourceConfigurationProperty(
                authentication_configuration=apprunner.CfnService.AuthenticationConfigurationProperty(
                    access_role_arn=access_role.role_arn
                ),
                auto_deployments_enabled=True,
                image_repository=apprunner.CfnService.ImageRepositoryProperty(
                    image_identifier=f"{vpc_stack.ecr_repos['app'].repository_uri}:latest",
                    #image_identifier=f"709825985650.dkr.ecr.us-east-1.amazonaws.com/fission-labs/flotorch-app:1.0.0",
                    image_repository_type="ECR",
                    image_configuration=apprunner.CfnService.ImageConfigurationProperty(
                        port="80",
                        runtime_environment_variables=env_vars
                    )
                )
            ),
            health_check_configuration=apprunner.CfnService.HealthCheckConfigurationProperty(
                protocol="HTTP",
                path="/health",
                interval=10,
                timeout=10,
                healthy_threshold=2,
                unhealthy_threshold=3
            ),
            instance_configuration=apprunner.CfnService.InstanceConfigurationProperty(
                cpu="4 vCPU",
                memory="12 GB",
                instance_role_arn=instance_role.role_arn
            ),
            network_configuration=apprunner.CfnService.NetworkConfigurationProperty(
                egress_configuration=apprunner.CfnService.EgressConfigurationProperty(
                    egress_type="VPC",
                    vpc_connector_arn=vpc_stack.vpc_connector.attr_vpc_connector_arn
                )
            )
        )

        # Outputs
        CfnOutput(
            self,
            "WebAppServiceUrl",
            value=webapp_service.attr_service_url,
            description="App Runner WebApp Service URL"
        )