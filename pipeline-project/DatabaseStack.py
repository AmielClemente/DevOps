"""
DatabaseStack.py - Contains DynamoDB table for alarm logging
"""
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
)
from constructs import Construct

class DatabaseStack(Stack):
    """
    DatabaseStack contains the DynamoDB table for alarm logging
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Table for Alarm Logs
        self.alarm_table = dynamodb.Table(
            self,
            "WebsiteAlarmTable",
            partition_key=dynamodb.Attribute(name="AlarmName", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="Timestamp", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        # Export the table name for other stacks
        self.alarm_table_name = self.alarm_table.table_name
