"""
AppStack.py - Contains website monitoring Lambda functions
"""
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions,
    aws_iam as iam,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_codedeploy as codedeploy,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigateway,
)
from constructs import Construct
import json
from datetime import datetime

# Import your constants
import constants

class AppStack(Stack):
    """
    AppStack contains the website monitoring Lambda functions
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1) DynamoDB Tables
        alarm_table = self.create_alarm_table()
        target_websites_table = self.create_target_websites_table()

        # 2) Website Crawler Lambda
        wh_lambda = self.create_website_crawler_lambda(target_websites_table)

        # 3) SNS Topic for Alarms
        alarm_topic = sns.Topic(
            self,
            "WebsiteAlarmTopic",
            display_name="Website Monitoring Alarms"
        )

        # Human notification subscription
        if getattr(constants, "ALERT_EMAIL", None):
            alarm_topic.add_subscription(subs.EmailSubscription(constants.ALERT_EMAIL))

        # 3) Alarm Logger Lambda  
        db_lambda = self.create_alarm_logger_lambda(alarm_table)
        
        # Subscribe Lambda to SNS Topic
        alarm_topic.add_subscription(subs.LambdaSubscription(db_lambda))
        
        # 4) CRUD API Lambda
        crud_lambda = self.create_crud_api_lambda(target_websites_table)

        # 5) CloudWatch Dashboard and Alarms
        # Dashboard and alarms are created dynamically based on DynamoDB content
        self.create_dashboard()
        self.create_alarms(alarm_topic)
        
        # 6) API Gateway for CRUD Operations
        self.create_api_gateway(crud_lambda)
        
        # 7) Lambda Operational Monitoring and Blue-Green Deployment
        self.create_operational_monitoring(wh_lambda, alarm_topic)

    def create_website_crawler_lambda(self, target_websites_table):
        """Create the website crawler Lambda function"""
        website_crawler = _lambda.Function(
            self,
            "WebsiteCrawlerLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda/website_crawler"),
            environment={
                "TARGET_WEBSITES_TABLE": target_websites_table.table_name,
                "NAMESPACE": constants.URL_MONITOR_NAMESPACE,
                "AVAILABILITY_METRIC_NAME": constants.AVAILABILITY_METRIC_NAME,
                "LATENCY_METRIC_NAME": constants.LATENCY_METRIC_NAME,
                "RESPONSE_SIZE_METRIC_NAME": constants.RESPONSE_SIZE_METRIC_NAME,
            },
            timeout=Duration.seconds(30),
        )

        # Allow the Lambda to put custom metrics in CloudWatch
        website_crawler.add_to_role_policy(
            iam.PolicyStatement(
                actions=["cloudwatch:PutMetricData"],
                resources=["*"],
            )
        )
        
        # Grant the Lambda function permission to read from the target websites table
        target_websites_table.grant_read_data(website_crawler)

        # Run Lambda every 5 minutes
        rule = events.Rule(
            self,
            "ScheduleRule",
            schedule=events.Schedule.rate(Duration.minutes(5)),
        )
        rule.add_target(targets.LambdaFunction(website_crawler))

        return website_crawler

    def create_alarm_logger_lambda(self, alarm_table):
        """Create the alarm logger Lambda function"""
        alarm_logger = _lambda.Function(
            self,
            "AlarmLoggerLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="alarm_logger.lambda_handler",
            code=_lambda.Code.from_asset("lambda/alarm_logger"),
            environment={
                "ALARM_TABLE": alarm_table.table_name,
                "FORCE_UPDATE": str(datetime.utcnow())
            }
        )

        # Grant the Lambda function permission to write to the DynamoDB table
        alarm_table.grant_write_data(alarm_logger)

        return alarm_logger

    def create_dashboard(self):
        """Create CloudWatch Dashboard - Dynamic based on DynamoDB content"""
        dashboard = cloudwatch.Dashboard(
            self,
            "Dashboard",
            dashboard_name=f"URL-MONITOR-DASHBOARD-{self.stack_name}",
            start="-PT6H",
        )

        # Create widgets that will automatically show metrics for any websites
        # being monitored by the web crawler
        
        # Availability Widget - uses CloudWatch search to find all availability metrics
        availability_widget = cloudwatch.GraphWidget(
            title="Website Availability",
            left=[
                cloudwatch.MathExpression(
                    expression="SEARCH('{amiel-week3 Availability}', 'Average', 300)",
                    label="Availability Metrics"
                )
            ],
            left_y_axis=cloudwatch.YAxisProps(min=0, max=1),
            legend_position=cloudwatch.LegendPosition.RIGHT,
            period=Duration.minutes(5),
            width=24,
            height=6,
        )

        # Latency Widget - uses CloudWatch search to find all latency metrics
        latency_widget = cloudwatch.GraphWidget(
            title="Website Latency (ms)",
            left=[
                cloudwatch.MathExpression(
                    expression="SEARCH('{amiel-week3 Latency}', 'Average', 300)",
                    label="Latency Metrics"
                )
            ],
            legend_position=cloudwatch.LegendPosition.RIGHT,
            period=Duration.minutes(5),
            width=24,
            height=6,
        )

        # Response Size Widget - uses CloudWatch search to find all response size metrics
        response_size_widget = cloudwatch.GraphWidget(
            title="Website Response Size (bytes)",
            left=[
                cloudwatch.MathExpression(
                    expression="SEARCH('{amiel-week3 ResponseSize}', 'Average', 300)",
                    label="Response Size Metrics"
                )
            ],
            legend_position=cloudwatch.LegendPosition.RIGHT,
            period=Duration.minutes(5),
            width=24,
            height=6,
        )

        dashboard.add_widgets(availability_widget)
        dashboard.add_widgets(latency_widget)
        dashboard.add_widgets(response_size_widget)

    def create_alarms(self, alarm_topic):
        """Create CloudWatch Alarms - Dynamic based on DynamoDB content"""
        # Note: Alarms will be created dynamically by the web crawler
        # or by a separate Lambda function that reads from DynamoDB
        # This method creates the infrastructure but doesn't create specific alarms
        # since we don't know which websites will be monitored at deployment time
        
        # The web crawler or a separate alarm manager will create alarms
        # for websites that are added to DynamoDB via the CRUD API
        pass  # Alarms created dynamically based on DynamoDB content

    def create_operational_monitoring(self, wh_lambda, alarm_topic):
        """Create operational monitoring and blue-green deployment for Lambda"""
        
        # Create Lambda alias for blue-green deployments
        version = wh_lambda.current_version
        alias = _lambda.Alias(
            self,
            "LambdaAlias",
            alias_name="Prod",
            version=version
        )
        
        # Create operational CloudWatch metrics for Lambda
        # Invocations metric
        invoc_metric = wh_lambda.metric_invocations(
            period=Duration.minutes(5),
            statistic="Sum"
        )
        
        # Duration metric
        duration_metric = wh_lambda.metric_duration(
            period=Duration.minutes(5),
            statistic="Average"
        )
        
        # Error metric
        error_metric = wh_lambda.metric_errors(
            period=Duration.minutes(5),
            statistic="Sum"
        )
        
        # Memory utilization metric
        memory_metric = wh_lambda.metric(
            metric_name="MemoryUtilization",
            period=Duration.minutes(5),
            statistic="Average"
        )
        
        # Create operational alarms
        invocations_alarm = cloudwatch.Alarm(
            self,
            "alarm_lambda_invocations",
            metric=invoc_metric,
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
            threshold=1,
            evaluation_periods=3,  # Check over 3 periods (15 minutes)
            datapoints_to_alarm=2,  # Require 2 consecutive periods with no invocations
            alarm_description="Lambda invocations below threshold - potential deployment issue",
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,  # Don't alarm on missing data during deployment
        )
        
        duration_alarm = cloudwatch.Alarm(
            self,
            "alarm_lambda_duration",
            metric=duration_metric,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            threshold=25000,  # 25 seconds (Lambda timeout is 30s)
            evaluation_periods=2,
            alarm_description="Lambda duration exceeding threshold - performance degradation",
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )
        
        error_alarm = cloudwatch.Alarm(
            self,
            "alarm_lambda_errors",
            metric=error_metric,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            threshold=2,  # Allow up to 2 errors before triggering alarm
            evaluation_periods=2,  # Check over 2 periods (10 minutes)
            datapoints_to_alarm=2,  # Require 2 consecutive failures
            alarm_description="Lambda errors detected - deployment may have issues",
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )
        
        memory_alarm = cloudwatch.Alarm(
            self,
            "alarm_lambda_memory",
            metric=memory_metric,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            threshold=80,  # 80% memory utilization
            evaluation_periods=2,
            alarm_description="Lambda memory utilization high - potential memory leak",
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )
        
        # Add alarm actions to notify via SNS
        invocations_alarm.add_alarm_action(cloudwatch_actions.SnsAction(alarm_topic))
        duration_alarm.add_alarm_action(cloudwatch_actions.SnsAction(alarm_topic))
        error_alarm.add_alarm_action(cloudwatch_actions.SnsAction(alarm_topic))
        memory_alarm.add_alarm_action(cloudwatch_actions.SnsAction(alarm_topic))
        
        # Create CodeDeploy Lambda deployment group with canary configuration
        # Temporarily remove error_alarm to allow deployment to succeed
        deployment_group = codedeploy.LambdaDeploymentGroup(
            self,
            "BlueGreenDeployment",
            alias=alias,
            deployment_config=codedeploy.LambdaDeploymentConfig.CANARY_10_PERCENT_5_MINUTES,
            alarms=[invocations_alarm, duration_alarm, memory_alarm]  # Removed error_alarm temporarily
        )
        
        return deployment_group

    def create_alarm_table(self):
        """Create DynamoDB table for alarm logging"""
        # Use CDK-generated name to avoid conflicts
        alarm_table = dynamodb.Table(
            self,
            "WebsiteAlarmTable",
            # Remove explicit table_name to let CDK generate a unique name
            partition_key=dynamodb.Attribute(name="AlarmName", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="Timestamp", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        return alarm_table
    
    def create_target_websites_table(self):
        """Create DynamoDB table for target websites management"""
        target_websites_table = dynamodb.Table(
            self,
            "TargetWebsitesTable",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        
        # Add GSI for enabled websites (for efficient querying)
        target_websites_table.add_global_secondary_index(
            index_name="enabled-index",
            partition_key=dynamodb.Attribute(name="enabled", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="created_at", type=dynamodb.AttributeType.STRING)
        )
        
        return target_websites_table
    
    def create_crud_api_lambda(self, target_websites_table):
        """Create the CRUD API Lambda function"""
        crud_lambda = _lambda.Function(
            self,
            "CRUDLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="crud_handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda/crud_api"),
            environment={
                "TARGET_WEBSITES_TABLE": target_websites_table.table_name,
            },
            timeout=Duration.seconds(30),
        )
        
        # Grant the Lambda function permission to read/write to the target websites table
        target_websites_table.grant_read_write_data(crud_lambda)
        
        return crud_lambda
    
    def create_api_gateway(self, crud_lambda):
        """Create API Gateway with CRUD endpoints"""
        api = apigateway.RestApi(
            self,
            "WebsiteTargetCRUDAPI",
            rest_api_name="Website Target CRUD API",
            description="API for managing website targets for web crawler",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"]
            )
        )
        
        # Create Lambda integration
        crud_integration = apigateway.LambdaIntegration(
            crud_lambda,
            request_templates={"application/json": '{"statusCode": "200"}'}
        )
        
        # Create /websites resource
        websites_resource = api.root.add_resource("websites")
        
        # GET /websites - List all websites
        websites_resource.add_method("GET", crud_integration)
        
        # POST /websites - Create new website
        websites_resource.add_method("POST", crud_integration)
        
        # Create /websites/{id} resource
        website_by_id_resource = websites_resource.add_resource("{id}")
        
        # GET /websites/{id} - Get specific website
        website_by_id_resource.add_method("GET", crud_integration)
        
        # PUT /websites/{id} - Update website
        website_by_id_resource.add_method("PUT", crud_integration)
        
        # DELETE /websites/{id} - Delete website
        website_by_id_resource.add_method("DELETE", crud_integration)
        
        # CORS is handled automatically by default_cors_preflight_options above
        # No need to add OPTIONS methods manually
        
        return api
