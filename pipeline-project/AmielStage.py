"""
AmielStage.py - Stage that combines AppStack and DatabaseStack
"""
from aws_cdk import Stage
from constructs import Construct
from AppStack import AppStack
from DatabaseStack import DatabaseStack

class AmielStage(Stage):
    """
    AmielStage combines both AppStack and DatabaseStack
    """
    
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Add both stacks to the stage
        database_stack = DatabaseStack(self, "DatabaseStack")
        app_stack = AppStack(self, "AppStack")
        
        # Pass the table name to the app stack
        # Note: In a real scenario, you might use cross-stack references
        # For now, we'll use a simple approach
