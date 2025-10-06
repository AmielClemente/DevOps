"""
teste_website.py - CDK Assertions Testing
Tests the CDK stack using assertions to verify resources
"""
import pytest
from aws_cdk import App, Environment
from aws_cdk import assertions
from AppStack import AppStack
from AmielStage import AmielStage

@pytest.fixture
def app():
    """PyTest fixture for CDK App"""
    return App()

@pytest.fixture
def app_stack(app):
    """PyTest fixture for AppStack"""
    return AppStack(app, "TestAppStack")

@pytest.fixture
def stage(app):
    """PyTest fixture for AmielStage"""
    return AmielStage(app, "TestStage")

def test_app_stack_lambda_functions(app_stack):
    """Test that AppStack creates 2 Lambda functions"""
    template = assertions.Template.from_stack(app_stack)
    
    # Check that we have 2 Lambda functions
    template.resource_count_is("AWS::Lambda::Function", 2)
    
    # Check specific Lambda functions exist
    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "lambda_function.lambda_handler",
        "Runtime": "python3.9"
    })
    
    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "alarm_logger.lambda_handler", 
        "Runtime": "python3.9"
    })

def test_app_stack_dynamodb_table(app_stack):
    """Test that AppStack creates DynamoDB table"""
    template = assertions.Template.from_stack(app_stack)
    
    # Check that we have 1 DynamoDB table
    template.resource_count_is("AWS::DynamoDB::Table", 1)
    
    # Check table properties
    template.has_resource_properties("AWS::DynamoDB::Table", {
        "BillingMode": "PAY_PER_REQUEST"
    })

def test_app_stack_cloudwatch_resources(app_stack):
    """Test that AppStack creates CloudWatch resources"""
    template = assertions.Template.from_stack(app_stack)
    
    # Check for CloudWatch Dashboard
    template.resource_count_is("AWS::CloudWatch::Dashboard", 1)
    
    # Check for CloudWatch Alarms (3 URLs * 3 alarm types = 9 + 4 operational = 13 alarms)
    template.resource_count_is("AWS::CloudWatch::Alarm", 13)
    
    # Check for EventBridge Rule
    template.resource_count_is("AWS::Events::Rule", 1)

def test_app_stack_sns_resources(app_stack):
    """Test that AppStack creates SNS resources"""
    template = assertions.Template.from_stack(app_stack)
    
    # Check for SNS Topic
    template.resource_count_is("AWS::SNS::Topic", 1)
    
    # Note: SNS TopicPolicy is not automatically created by CDK

def test_stage_contains_all_resources(app_stack):
    """Test that AppStack contains all resources"""
    template = assertions.Template.from_stack(app_stack)
    
    # Check that we have both Lambda functions and DynamoDB table
    template.resource_count_is("AWS::Lambda::Function", 2)
    template.resource_count_is("AWS::DynamoDB::Table", 1)
    
    # Check total resources
    # AppStack: 2 Lambda + 1 Dashboard + 13 Alarms + 1 Rule + 1 Topic + 1 Table + CodeDeploy resources
    template.resource_count_is("AWS::Lambda::Function", 2)
    template.resource_count_is("AWS::DynamoDB::Table", 1)
    template.resource_count_is("AWS::CloudWatch::Dashboard", 1)
    template.resource_count_is("AWS::CloudWatch::Alarm", 13)
    template.resource_count_is("AWS::Events::Rule", 1)
    template.resource_count_is("AWS::SNS::Topic", 1)

def test_lambda_environment_variables(app_stack):
    """Test that Lambda functions have correct environment variables"""
    template = assertions.Template.from_stack(app_stack)
    
    # Check website crawler Lambda environment
    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "lambda_function.lambda_handler",
        "Environment": {
            "Variables": {
                "NAMESPACE": "amiel-week3"
            }
        }
    })
    
    # Check alarm logger Lambda environment (ALARM_TABLE is now a CloudFormation reference)
    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "alarm_logger.lambda_handler",
        "Environment": {
            "Variables": {
                "ALARM_TABLE": {
                    "Ref": "WebsiteAlarmTable214A7BFF"  # CloudFormation reference
                }
            }
        }
    })

def test_iam_permissions(app_stack):
    """Test that Lambda functions have correct IAM permissions"""
    template = assertions.Template.from_stack(app_stack)
    
    # Check for IAM roles (2 Lambda roles + CodeDeploy roles = 3+ roles)
    template.resource_count_is("AWS::IAM::Role", 3)  # Updated count
    
    # Check for IAM policies
    template.resource_count_is("AWS::IAM::Policy", 2)  # One for each Lambda

def test_dynamodb_table_structure(app_stack):
    """Test DynamoDB table has correct structure"""
    template = assertions.Template.from_stack(app_stack)
    
    # Check table key schema
    template.has_resource_properties("AWS::DynamoDB::Table", {
        "KeySchema": [
            {
                "AttributeName": "AlarmName",
                "KeyType": "HASH"
            },
            {
                "AttributeName": "Timestamp", 
                "KeyType": "RANGE"
            }
        ]
    })

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
