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

class PipelineProjectStackV2(Stack):
    """CI/CD Pipeline for Website Monitoring Application - Version 2"""

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
                "echo '=== DEBUGGING DIRECTORY STRUCTURE ==='",
                "ls -la",
                "echo '=== PIPELINE-PROJECT DIRECTORY ==='",
                "ls -la pipeline-project/",
                "echo '=== TESTS DIRECTORY ==='",
                "ls -la pipeline-project/tests/",
                "echo '=== RUNNING TESTS ==='",
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

        # Simplified test stage - just run all tests together
        test_stage = ShellStep(
            "AllTests",
            commands=[
                "echo 'Running all tests...'",
                "pip install -r pipeline-project/requirements.txt",
                "pip install pytest boto3 requests",
                "python -m pytest pipeline-project/tests/ -v --tb=short",
                "echo 'All tests passed!'"
            ]
        )

        # Alpha stage
        alpha = AmielStage(self, 'alpha', 
            env=Environment(
                account=self.account,
                region=self.region
            )
        )
        
        pipeline.add_stage(alpha, pre=[test_stage])
