from aws_cdk import (
    Stack,
    Stage,
    Environment,
    SecretValue,
)
from aws_cdk import pipelines
from aws_cdk.pipelines import CodePipelineSource, ShellStep, ManualApprovalStep
from aws_cdk import aws_iam as iam
from constructs import Construct

# Import the stage
from AmielStage import AmielStage

class PipelineProjectStackV2(Stack):


    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # GitHub source
        source = CodePipelineSource.git_hub(
            repo_string="AmielClemente/DevOps",  
            branch="main",
            action_name="DevOps",
            authentication=SecretValue.secrets_manager("DevOps") 
        )

        # Build commands - only build/synth, no tests
        synth = ShellStep(
            "BuildCommands",
            input=source,
            commands=[
                "npm install -g aws-cdk",
                "pip install -r pipeline-project/requirements.txt",
                "echo '=== DEBUGGING DIRECTORY STRUCTURE ==='",
                "ls -la",
                "echo '=== PIPELINE-PROJECT DIRECTORY ==='",
                "ls -la pipeline-project/",
                "echo '=== BUILDING CDK STACK ==='",
                "cd pipeline-project && cdk synth"
            ],
            primary_output_directory = "pipeline-project/cdk.out"
        )

        # Create pipeline
        pipeline = pipelines.CodePipeline(
            self, "AmielPipelineV2",
            synth=synth
        )

        # Unit Tests - Test individual components in isolation
        unit_tests = ShellStep(
            "UnitTests",
            commands=[
                "echo 'Running Unit Tests...'",
                "export JSII_SILENCE_WARNING_DEPRECATED_NODE_VERSION=1",
                "pip install -r pipeline-project/requirements.txt",
                "pip install pytest boto3 requests",
                "echo '=== Running Lambda Function Unit Tests ==='",
                "python -m pytest pipeline-project/tests/test_simple.py::test_1_unit_basic_functionality -v",
                "python -m pytest pipeline-project/tests/test_simple.py::test_2_unit_error_handling -v",
                "python -m pytest pipeline-project/tests/test_simple.py::test_3_unit_timeout_handling -v",
                "python -m pytest pipeline-project/tests/test_simple.py::test_4_unit_cloudwatch_data_validation -v",
                "python -m pytest pipeline-project/tests/test_simple.py::test_5_unit_environment_variables -v",
                "echo 'Unit tests completed successfully'"
            ]
        )

        # Functional Tests - Test complete workflows end-to-end
        functional_tests = ShellStep(
            "FunctionalTests",
            commands=[
                "echo 'Running Functional Tests...'",
                "export JSII_SILENCE_WARNING_DEPRECATED_NODE_VERSION=1",
                "pip install -r pipeline-project/requirements.txt",
                "pip install pytest boto3 requests",
                "echo '=== Running Lambda Function Functional Tests ==='",
                "python -m pytest pipeline-project/tests/test_simple.py::test_1_functional_end_to_end_flow -v",
                "python -m pytest pipeline-project/tests/test_simple.py::test_2_functional_multi_website_monitoring -v",
                "python -m pytest pipeline-project/tests/test_simple.py::test_3_functional_performance_measurement -v",
                "python -m pytest pipeline-project/tests/test_simple.py::test_4_functional_mixed_scenarios -v",
                "python -m pytest pipeline-project/tests/test_simple.py::test_5_functional_complete_monitoring_cycle -v",
                "echo 'Functional tests completed successfully'"
            ]
        )

        # Infrastructure Tests - Test CDK infrastructure creation
        infrastructure_tests = ShellStep(
            "InfrastructureTests",
            commands=[
                "echo 'Running Infrastructure Tests...'",
                "export JSII_SILENCE_WARNING_DEPRECATED_NODE_VERSION=1",
                "pip install -r pipeline-project/requirements.txt",
                "pip install pytest boto3",
                "echo '=== Checking Python and CDK versions ==='",
                "python --version",
                "node --version",
                "pip list | grep -E '(aws-cdk|constructs|jsii)'",
                "echo '=== Testing CDK Synthesis First ==='",
                "cd pipeline-project",
                "python -c \"from AppStack import AppStack; from aws_cdk import App; app = App(); stack = AppStack(app, 'TestStack'); print('CDK synthesis test passed')\"",
                "echo '=== Running CDK Infrastructure Tests ==='",
                "python -m pytest tests/teste_website.py -v --tb=short",
                "echo 'Infrastructure tests completed successfully'"
            ]
        )

        # Real Integration Tests - Test actual AWS service interactions
        real_integration_tests = ShellStep(
            "RealIntegrationTests",
            commands=[
                "echo 'Running Real Integration Tests...'",
                "export JSII_SILENCE_WARNING_DEPRECATED_NODE_VERSION=1",
                "pip install -r pipeline-project/requirements.txt",
                "pip install pytest boto3",
                "echo '=== Running Real AWS Integration Tests ==='",
                "python -m pytest pipeline-project/tests/test_integration.py -v",
                "echo 'Real integration tests completed successfully'"
            ]
        )

        # Alpha stage (Development)
        alpha = AmielStage(self, 'alpha', 
            env=Environment(
                account=self.account,
                region=self.region
            )
        )
        
        # Beta stage (Staging)
        beta = AmielStage(self, 'beta', 
            env=Environment(
                account=self.account,
                region=self.region
            )
        )
        
        # Gamma stage (Pre-Production)
        gamma = AmielStage(self, 'gamma', 
            env=Environment(
                account=self.account,
                region=self.region
            )
        )
        
        # Production stage (Live)
        prod = AmielStage(self, 'prod', 
            env=Environment(
                account=self.account,
                region=self.region
            )
        )
        
        # Add stages to pipeline with appropriate test blockers
        # Alpha (Development) - Unit Tests only
        pipeline.add_stage(alpha, pre=[unit_tests])
        
        # Beta (Staging) - Functional Tests only
        pipeline.add_stage(beta, pre=[functional_tests])
        
        # Gamma (Pre-Production) - Integration Tests only
        pipeline.add_stage(gamma, pre=[real_integration_tests])
        
        # Production (Live) - Manual approval + Infrastructure Tests
        manual_approval = ManualApprovalStep(
            "ProductionApproval",
            comment="Please review and approve deployment to production environment"
        )
        pipeline.add_stage(prod, pre=[manual_approval, infrastructure_tests])
        
        # Add AWS service permissions to CodeBuild role for integration tests
        # This must be done after all stages are added
        pipeline.build_pipeline()
        pipeline.pipeline.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AWSCloudFormationReadOnlyAccess")
        )
        pipeline.pipeline.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBReadOnlyAccess")
        )
        pipeline.pipeline.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AWSLambda_ReadOnlyAccess")
        )
        pipeline.pipeline.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchReadOnlyAccess")
        )
        pipeline.pipeline.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSNSReadOnlyAccess")
        )
