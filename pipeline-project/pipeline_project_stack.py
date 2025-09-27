from aws_cdk import (
    Stack,
    Stage,
    Environment,
    SecretValue,
)
from aws_cdk import pipelines
from aws_cdk.pipelines import CodePipelineSource, ShellStep
from constructs import Construct

# Import the stage
from AmielStage import AmielStage

class PipelineProjectStack(Stack):
    """CI/CD Pipeline for Website Monitoring Application"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # GitHub source
        source = CodePipelineSource.git_hub(
            repo_string="AmielClemente/DevOps",  # Replace with your repo
            branch="main",
            action_name="DevOps",
            authentication=SecretValue.secrets_manager("DevOps")  # Your secret name
        )

        # Build commands with testing
        synth = ShellStep(
            "BuildCommands",
            input=source,
            commands=[
                "npm install -g aws-cdk",
                "pip install -r pipeline-project/requirements.txt",
                "pip install pytest boto3",
                "echo 'Running tests...'",
                "python -m pytest pipeline-project/tests/ -v --tb=short",
                "echo 'Tests completed successfully'",
                "cd pipeline-project && cdk synth"
            ],
            primary_output_directory = "pipeline-project/cdk.out"
        )

        # Create pipeline
        pipeline = pipelines.CodePipeline(
            self, "AmielPipeline",
            synth=synth
        )

        # Unit Tests Stage
        unit_test = ShellStep(
            "UnitTests",
            commands=[
                "echo 'Running unit tests...'",
                "pip install pytest boto3",
                "python -m pytest pipeline-project/tests/test_simple.py::test_1_unit_basic_functionality pipeline-project/tests/test_simple.py::test_2_unit_error_handling pipeline-project/tests/test_simple.py::test_3_unit_timeout_handling pipeline-project/tests/test_simple.py::test_4_unit_cloudwatch_data_validation pipeline-project/tests/test_simple.py::test_5_unit_environment_variables -v --tb=short",
                "echo 'Unit tests passed!'"
            ]
        )

        # Functional Tests Stage  
        functional_test = ShellStep(
            "FunctionalTests",
            commands=[
                "echo 'Running functional tests...'",
                "pip install pytest boto3",
                "python -m pytest pipeline-project/tests/test_simple.py::test_1_functional_end_to_end_flow pipeline-project/tests/test_simple.py::test_2_functional_multi_website_monitoring pipeline-project/tests/test_simple.py::test_3_functional_performance_measurement pipeline-project/tests/test_simple.py::test_4_functional_mixed_scenarios pipeline-project/tests/test_simple.py::test_5_functional_complete_monitoring_cycle -v --tb=short",
                "echo 'Functional tests passed!'"
            ]
        )

        # Beta stage
        beta = AmielStage(self, 'beta', 
            env=Environment(
                account=self.account,
                region=self.region
            )
        )
        
        # Gamma stage
        gamma = AmielStage(self, 'gamma', 
            env=Environment(
                account=self.account,
                region=self.region
            )
        )
        
        # Production stage
        prod = AmielStage(self, 'prod', 
            env=Environment(
                account=self.account,
                region=self.region
            )
        )
        
        # Add stages to pipeline with test blockers
        pipeline.add_stage(beta, pre=[unit_test, functional_test])
        pipeline.add_stage(gamma, pre=[unit_test, functional_test])
        pipeline.add_stage(prod, pre=[unit_test, functional_test])
