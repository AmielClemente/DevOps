"""
AmielStage.py - Stage that contains the complete website monitoring application
"""
from aws_cdk import Stage
from constructs import Construct
from AppStack import AppStack

class AmielStage(Stage):
    """
    AmielStage contains the complete website monitoring application
    including Lambda functions, DynamoDB table, CloudWatch alarms, and CodeDeploy
    """
    
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the complete application stack
        app_stack = AppStack(self, "AppStack")
