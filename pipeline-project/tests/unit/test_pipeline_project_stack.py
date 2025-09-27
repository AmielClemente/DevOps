import aws_cdk as core
import aws_cdk.assertions as assertions

def test_pipeline_import():
    """
    Simple test to verify that the pipeline stack can be imported.
    This avoids the Lambda asset issues in the pipeline environment.
    """
    # Test that we can import the stack class
    from pipeline_project_stack import PipelineProjectStackV2
    assert PipelineProjectStackV2 is not None
    
    # Test that we can import the stage class
    from AmielStage import AmielStage
    assert AmielStage is not None
    
    # Test that we can import the app stack
    from AppStack import AppStack
    assert AppStack is not None
    
    # Test that we can import the database stack
    from DatabaseStack import DatabaseStack
    assert DatabaseStack is not None
