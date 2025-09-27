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
                "pip install -r requirements.txt",
                "pip install pytest boto3",
                "echo 'Running tests...'",
                "python -m pytest tests/ -v --tb=short",
                "echo 'Tests completed successfully'",
                "cdk synth"
            ],
            primary_output_directory = "cdk.out"
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
                "python -m pytest tests/test_website_monitor.py -v --tb=short",
                "echo 'Unit tests passed!'"
            ]
        )

        # Functional Tests Stage  
        functional_test = ShellStep(
            "FunctionalTests",
            commands=[
                "echo 'Running functional tests...'",
                "pip install pytest boto3",
                "python -m pytest tests/test_web_crawler_comprehensive.py -v --tb=short",
                "echo 'Functional tests passed!'"
            ]
        )

        # Alpha stage
        alpha = AmielStage(self, 'alpha', 
            env=Environment(
                account=self.account,
                region=self.region
            )
        )
        
        pipeline.add_stage(alpha, pre=[unit_test, functional_test])
