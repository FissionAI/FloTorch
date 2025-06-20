pipeline {
    agent {
        docker {
            image 'ubuntu:latest'
            args '-u root'
        }
    }

    parameters {
        string(name: 'AWS_REGION', defaultValue: 'us-east-1', description: 'AWS Region (e.g., us-east-1)')
        string(name: 'PROJECT_NAME', defaultValue: 'flotorch', description: 'Project Name (e.g., flotorch)')
        string(name: 'TABLE_SUFFIX', defaultValue: '', description: 'Unique Table Suffix (6 lowercase letters)')
        string(name: 'CLIENT_NAME', defaultValue: 'flotorch', description: 'Client Name (e.g., flotorch)')
        string(name: 'CREATED_BY', defaultValue: 'DevOpsTeam', description: 'Created by (e.g., DevOpsTeam)')
	string(name: 'TEMPLATE_VERSION', defaultValue: 'v1.0.0', description: 'Template Version (e.g., 2.0.1)')
        string(name: 'OPENSEARCH_ADMIN_USER', defaultValue: 'admin', description: 'OpenSearch Admin Username')
        password(name: 'OPENSEARCH_ADMIN_PASSWORD', description: 'OpenSearch Admin Password')
        password(name: 'NGINX_AUTH_PASSWORD', description: 'Nginx Auth Password')
    }

    environment {
        AWS_REGION = "${params.AWS_REGION}"
        PROJECT_NAME = "${params.PROJECT_NAME}"
        TABLE_SUFFIX = "${params.TABLE_SUFFIX}"
        CLIENT_NAME = "${params.CLIENT_NAME}"
        CREATED_BY = "${params.CREATED_BY}"
	TEMPLATE_VERSION = "${params.TEMPLATE_VERSION}"
        OPENSEARCH_ADMIN_USER = "${params.OPENSEARCH_ADMIN_USER}"
        OPENSEARCH_ADMIN_PASSWORD = "${params.OPENSEARCH_ADMIN_PASSWORD}"
        NGINX_AUTH_PASSWORD = "${params.NGINX_AUTH_PASSWORD}"
    }

    stages {
        stage('Install dependencies') {
            steps {
                script {
                    sh '''
                        echo "Installing AWS CLI..."
                        apt-get update
                        apt-get install -y unzip curl

                        # Check if AWS CLI is already installed
                        if ! command -v aws &> /dev/null; then
                            echo "AWS CLI not found. Installing..."
                            curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                            unzip -o -q awscliv2.zip
                            ./aws/install --update
                        else
                            echo "AWS CLI is already installed"
                            aws --version
                        fi

                        # Verify AWS CLI installation
                        aws --version || {
                            echo "AWS CLI installation failed"
                            exit 1
                        }
                        echo "AWS CLI installation successful"
                    '''
                }
            }
        }

        stage('Checkout Repository') {
            steps {
                script {
                    git branch: 'main', url: 'https://github.com/FissionAI/FloTorch.git'
                }
            }
        }

        stage('Deploy FloTorch Master Stack') {
            steps {
                withAWS(credentials: 'aws-creds', region: env.AWS_REGION) {
                    sh '''
                        echo "Starting FloTorch Stack Deployment..."

                        aws cloudformation create-stack \
                            --region ${AWS_REGION} \
                            --stack-name flotorch-stack \
                            --template-url https://flotorch-public.s3.amazonaws.com/${TEMPLATE_VERSION}/templates/master-template.yaml \
                            --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
                            --parameters \
                                ParameterKey=ProjectName,ParameterValue=${PROJECT_NAME} \
                                ParameterKey=TableSuffix,ParameterValue=${TABLE_SUFFIX} \
                                ParameterKey=ClientName,ParameterValue=${CLIENT_NAME} \
                                ParameterKey=CreatedBy,ParameterValue=${CREATED_BY} \
				ParameterKey=TemplateVersion,ParameterValue=${TEMPLATE_VERSION} \
                                ParameterKey=OpenSearchAdminUser,ParameterValue=${OPENSEARCH_ADMIN_USER} \
                                ParameterKey=OpenSearchAdminPassword,ParameterValue=${OPENSEARCH_ADMIN_PASSWORD} \
                                ParameterKey=NginxAuthPassword,ParameterValue=${NGINX_AUTH_PASSWORD} \
                                ParameterKey=PrerequisitesMet,ParameterValue=yes

                        echo "Waiting for stack creation to complete..."
                        aws cloudformation wait stack-create-complete \
                            --stack-name flotorch-stack \
                            --region ${AWS_REGION}

                        echo "CloudFormation Stack Deployment Successful!"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "FloTorch Stack deployed successfully!"
        }
        failure {
            echo "Deployment failed!"
        }
    }
}
