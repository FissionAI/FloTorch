from typing import List, Dict, Optional, Any
import boto3, yaml, uuid
from botocore.exceptions import ClientError

class BedrockGuardrails:
    def __init__(self):
        self.bedrock_client = boto3.client('bedrock')
        self.runtime_client = boto3.client('bedrock-runtime')

    def create_guardrail(
        self,
        guardrail_config: dict
    ) -> Dict:
        """
        Create a comprehensive guardrail using Amazon Bedrock
        
        Args:
            name: Name of the guardrail
            description: Description of the guardrail
            content_policy: Content policy configuration
            topic_policy: Topic policy configuration
            word_policy: Word policy configuration
            sensitive_info_policy: Sensitive information policy configuration
            contextual_grounding_policy: Contextual grounding policy configuration
            input_filter: Input filtering configuration
            output_filter: Output filtering configuration
        """
        try:

            response = self.bedrock_client.create_guardrail(**guardrail_config)
            return response

        except ClientError as e:
            print(f"Error creating guardrail: {str(e)}")
            raise

    def apply_guardrail(
        self,
        guardrail_id: str,
        guardrail_version: str,
        content: str,
        source: str = 'INPUT',
        model_id: str = None,
        inference_configuration: Dict = None
    ) -> Dict:
        """
        Apply a guardrail to content using Amazon Bedrock ApplyGuardrails API
        
        Args:
            guardrail_id (str): The unique identifier of the guardrail
            guardrail_version (str): The version of the guardrail to apply
            content (str): The content to validate against the guardrail
            source (str): The source of the content ('INPUT' or 'OUTPUT')
            model_id (str, optional): The model identifier to use for inference
            inference_configuration (Dict, optional): Additional inference configuration parameters
            
        Returns:
            Dict: Response from the ApplyGuardrails API
            
        Example response structure:
        {
            'results': [{
                'status': 'ALLOWED'|'FILTERED'|'DENIED',
                'statusMessage': 'string',
                'violations': [{
                    'policyName': 'string',
                    'violationType': 'string',
                    'violationMessage': 'string'
                }]
            }],
            'responseMetadata': {
                'requestId': 'string',
                'attempts': 123,
                'totalRetryDelay': 123.0
            }
        }
        """
        try:
            request_params = {
                'guardrailIdentifier': guardrail_id,
                'guardrailVersion': guardrail_version,
                'source': source,
                'content': content
            }

            response = self.runtime_client.apply_guardrail(**request_params)
            return response

        except ClientError as e:
            print(f"Error applying guardrail: {str(e)}")
            raise
    
    def load_guardrail_config_from_yaml(self, yaml_file_path: str) -> Dict[str, Any]:
        """
        Loads guardrail configuration from a YAML file and converts it to Bedrock-compatible format.
        
        Args:
            yaml_file_path (str): Path to the YAML configuration file
            
        Returns:
            Dict[str, Any]: Bedrock-compatible guardrail configuration
        """
        try:
            with open(yaml_file_path, 'r') as file:
                yaml_config = yaml.safe_load(file)
                
            if not yaml_config or 'guardrails' not in yaml_config:
                raise ValueError("Invalid YAML configuration: 'guardrails' section not found")
                
            config = yaml_config['guardrails']
            
            bedrock_config = {}

            if 'name' in config:
                random_suffix = str(uuid.uuid4())[:4] 
                bedrock_config['name'] = f"{config['name']}-{random_suffix}"

            if 'description' in config:
                bedrock_config['description'] = config['description']
            
            # Convert content policy
            if 'content_policy' in config:
                bedrock_config['contentPolicyConfig'] = {
                    'filtersConfig': config['content_policy']['filtersConfig']
                }
                
            # Convert topic policy
            if 'topic_policy' in config:
                bedrock_config['topicPolicyConfig'] = {
                    'topicsConfig': config['topic_policy']['topicsConfig']
                }
                
            # Convert word policy
            if 'word_policy' in config:
                bedrock_config['wordPolicyConfig'] = {
                    'wordsConfig': config['word_policy'].get('wordsConfig', []),
                    'managedWordListsConfig': config['word_policy'].get('managedWordListsConfig', [])
                }
                
            # Convert sensitive info policy
            if 'sensitive_info_policy' in config:
                bedrock_config['sensitiveInformationPolicyConfig'] = {
                    'piiEntitiesConfig': config['sensitive_info_policy'].get('piiEntitiesConfig', []),
                    'regexesConfig': config['sensitive_info_policy'].get('regexesConfig', [])
                }
                
            # Convert contextual grounding policy
            if 'contextual_grounding_policy' in config:
                bedrock_config['contextualGroundingPolicyConfig'] = {
                    'filtersConfig': config['contextual_grounding_policy']['filtersConfig']
                }
                
            # Convert filter messages
            if 'blocked_input_message' in config:
                bedrock_config['blockedInputMessaging'] = config['blocked_input_message']
                
            if 'blocked_outputs_message' in config:
                bedrock_config['blockedOutputsMessaging'] = config['blocked_outputs_message']
                
            return bedrock_config
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {yaml_file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing configuration: {str(e)}")

# Example configurations for different policy types 
def get_comprehensive_guardrail_config():
    """
    Complete guardrail configuration with all policy types
    """
    # Content Policy Configuration
    content_policy = {
        'filtersConfig': [{
            'type': 'HATE', #'SEXUAL'|'VIOLENCE'|'HATE'|'INSULTS'|'MISCONDUCT'|'PROMPT_ATTACK'
            'inputStrength': 'LOW', #'NONE'|'LOW'|'MEDIUM'|'HIGH'
            'outputStrength': 'LOW', #'NONE'|'LOW'|'MEDIUM'|'HIGH',
            'inputModalities': [
                'TEXT' #'TEXT'|'IMAGE'
            ],
            'outputModalities': [
                'TEXT' #'TEXT'|'IMAGE'
            ]
        }]
    }

    # Topic Policy Configuration
    topic_policy = {
        'topicsConfig': [{
            'name': 'Financial Advice',
            'definition': 'Providing financial or investment advice',
            'examples': [
                'What stocks should I invest in?',
                'How should I invest my money?'
            ],
            'type': 'DENY'
        }, {
            'name': 'Medical Advice',
            'definition': 'Providing medical diagnosis or treatment advice',
            'examples': [
                'What medication should I take?',
                'How should I treat this condition?'
            ],
            'type': 'DENY'
        }]
    }

    # Word Policy Configuration
    word_policy = {
       'wordsConfig': [
            {
                'text': 'crazy' #Any string
            },
        ],
        'managedWordListsConfig': [
            {
                'type': 'PROFANITY'
            },
        ]
    }

    # Sensitive Information Policy Configuration
    sensitive_info_policy = {
        'piiEntitiesConfig': [{
            'type': 'EMAIL_ADDRESS', #'ADDRESS'|'AGE'|'AWS_ACCESS_KEY'|'AWS_SECRET_KEY'|'CA_HEALTH_NUMBER'|'CA_SOCIAL_INSURANCE_NUMBER'|'CREDIT_DEBIT_CARD_CVV'|'CREDIT_DEBIT_CARD_EXPIRY'|'CREDIT_DEBIT_CARD_NUMBER'|'DRIVER_ID'|'EMAIL'|'INTERNATIONAL_BANK_ACCOUNT_NUMBER'|'IP_ADDRESS'|'LICENSE_PLATE'|'MAC_ADDRESS'|'NAME'|'PASSWORD'|'PHONE'|'PIN'|'SWIFT_CODE'|'UK_NATIONAL_HEALTH_SERVICE_NUMBER'|'UK_NATIONAL_INSURANCE_NUMBER'|'UK_UNIQUE_TAXPAYER_REFERENCE_NUMBER'|'URL'|'USERNAME'|'US_BANK_ACCOUNT_NUMBER'|'US_BANK_ROUTING_NUMBER'|'US_INDIVIDUAL_TAX_IDENTIFICATION_NUMBER'|'US_PASSPORT_NUMBER'|'US_SOCIAL_SECURITY_NUMBER'|'VEHICLE_IDENTIFICATION_NUMBER'
            'mode': 'BLOCK' # 'BLOCK'|'ANONYMIZE'
        }, {
            'type': 'PHONE_NUMBER',
            'mode': 'BLOCK'
        }, {
            'type': 'CREDIT_DEBIT_NUMBER',
            'mode': 'ANONYMIZE'
        }, {
            'type': 'SSN',
            'mode': 'ANONYMIZE'
        }],
        'regexesConfig': [{
            'name': 'SSN', #Any string
            'pattern': r'\b\d{3}-\d{2}-\d{4}\b', #Any string
            'description': 'SSN pattern', #Any string
            'action': 'BLOCK'  # 'BLOCK'|'ANONYMIZE'
        }]
    }

    # Contextual Grounding Policy Configuration
    contextual_grounding_policy = {
         'filtersConfig': [
            {
                'type': 'GROUNDING', #'GROUNDING'|'RELEVANCE'
                'threshold': 123.0 # Value
            },
        ]
    }

    input_filter = 'This input contains restricted content.'

    output_filter = 'This output contains restricted content.'

    return {
        'content_policy': content_policy,
        'topic_policy': topic_policy,
        'word_policy': word_policy,
        'sensitive_info_policy': sensitive_info_policy,
        'contextual_grounding_policy': contextual_grounding_policy,
        'input_filter': input_filter,
        'output_filter': output_filter
    }

# Example configurations
def create_domain_specific_guardrail():
    """
    Create a domain-specific guardrail with all policy types
    """
    guardrails = BedrockGuardrails()
    config = get_comprehensive_guardrail_config()

    response = guardrails.create_guardrail(
        name='ComprehensiveGuardrail',
        description='Complete guardrail with all policy configurations',
        **config
    )
    return response
