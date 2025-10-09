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

        # 1) DynamoDB Table for Alarm Logging
        alarm_table = self.create_alarm_table()

        # 2) Website Crawler Lambda
        wh_lambda = self.create_website_crawler_lambda()

        # 3) Alarm Logger Lambda  
        db_lambda = self.create_alarm_logger_lambda(alarm_table)

        # 3) SNS Topic for Alarms
        alarm_topic = sns.Topic(
            self,
            "WebsiteAlarmTopic",
            display_name="Website Monitoring Alarms"
        )

        # Human notification subscription
        if getattr(constants, "ALERT_EMAIL", None):
            alarm_topic.add_subscription(subs.EmailSubscription(constants.ALERT_EMAIL))

        # Subscribe Lambda to SNS Topic
        alarm_topic.add_subscription(subs.LambdaSubscription(db_lambda))

        # 4) CloudWatch Dashboard
        self.create_dashboard()

        # 5) CloudWatch Alarms
        self.create_alarms(alarm_topic)
        
        # 6) Lambda Operational Monitoring and Blue-Green Deployment
        self.create_operational_monitoring(wh_lambda, alarm_topic)

    def create_website_crawler_lambda(self):
        """Create the website crawler Lambda function"""
        website_crawler = _lambda.Function(
            self,
            "WebsiteCrawlerLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(
                "lambda/website_crawler",
                bundling=_lambda.BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_9.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output"
                    ],
                ),
            ),
            environment={
                "URLS": json.dumps(constants.URLS),
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
        """Create CloudWatch Dashboard"""
        dashboard = cloudwatch.Dashboard(
            self,
            "Dashboard",
            dashboard_name=f"URL-MONITOR-DASHBOARD-{self.stack_name}",
            start="-PT6H",
        )

        avail_series = []
        latency_series = []
        size_series = []

        # Create metrics for each URL
        for idx, url in enumerate(constants.URLS, start=1):
            dimensions_map = {"URL": url}

            # Metrics
            avail_metric = cloudwatch.Metric(
                namespace=constants.URL_MONITOR_NAMESPACE,
                metric_name=constants.AVAILABILITY_METRIC_NAME,
                dimensions_map=dimensions_map,
                period=Duration.minutes(1),
                label=f"Availability: {url}",
                statistic="Average",
            )

            latency_metric = cloudwatch.Metric(
                namespace=constants.URL_MONITOR_NAMESPACE,
                metric_name=constants.LATENCY_METRIC_NAME,
                dimensions_map=dimensions_map,
                period=Duration.minutes(1),
                label=f"Latency (ms): {url}",
                statistic="Average",
            )

            response_size_metric = cloudwatch.Metric(
                namespace=constants.URL_MONITOR_NAMESPACE,
                metric_name=constants.RESPONSE_SIZE_METRIC_NAME,
                dimensions_map=dimensions_map,
                period=Duration.minutes(1),
                label=f"Response Size (bytes): {url}",
                statistic="Average",
            )

            avail_series.append(avail_metric)
            latency_series.append(latency_metric)
            size_series.append(response_size_metric)

        # Dashboard Widgets
        availability_widget = cloudwatch.GraphWidget(
            title="Availability (all URLs)",
            left=avail_series,
            left_y_axis=cloudwatch.YAxisProps(min=0, max=1),
            legend_position=cloudwatch.LegendPosition.RIGHT,
            period=Duration.minutes(1),
            width=24,
            height=6,
        )

        latency_widget = cloudwatch.GraphWidget(
            title="Latency (ms) — all URLs",
            left=latency_series,
            legend_position=cloudwatch.LegendPosition.RIGHT,
            period=Duration.minutes(1),
            width=24,
            height=6,
        )

        response_size_widget = cloudwatch.GraphWidget(
            title="Response Size (bytes) — all URLs",
            left=size_series,
            legend_position=cloudwatch.LegendPosition.RIGHT,
            period=Duration.minutes(1),
            width=24,
            height=6,
        )

        dashboard.add_widgets(availability_widget)
        dashboard.add_widgets(latency_widget)
        dashboard.add_widgets(response_size_widget)

    def create_alarms(self, alarm_topic):
        """Create CloudWatch Alarms"""
        # Create metrics, alarms per URL
        for idx, url in enumerate(constants.URLS, start=1):
            dimensions_map = {"URL": url}

            # Metrics
            avail_metric = cloudwatch.Metric(
                namespace=constants.URL_MONITOR_NAMESPACE,
                metric_name=constants.AVAILABILITY_METRIC_NAME,
                dimensions_map=dimensions_map,
                period=Duration.minutes(1),
                statistic="Average",
            )

            latency_metric = cloudwatch.Metric(
                namespace=constants.URL_MONITOR_NAMESPACE,
                metric_name=constants.LATENCY_METRIC_NAME,
                dimensions_map=dimensions_map,
                period=Duration.minutes(1),
                statistic="Average",
            )

            response_size_metric = cloudwatch.Metric(
                namespace=constants.URL_MONITOR_NAMESPACE,
                metric_name=constants.RESPONSE_SIZE_METRIC_NAME,
                dimensions_map=dimensions_map,
                period=Duration.minutes(1),
                statistic="Average",
            )

            # Alarms
            availability_alarm = cloudwatch.Alarm(
                self,
                f"AvailabilityAlarm{idx}",
                metric=avail_metric,
                threshold=constants.AVAIL_THRESHOLD,
                comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                alarm_description=f"Availability below {constants.AVAIL_THRESHOLD*100:.0f}% for {url}",
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
            )
            availability_alarm.add_alarm_action(cloudwatch_actions.SnsAction(alarm_topic))

            latency_alarm = cloudwatch.Alarm(
                self,
                f"LatencyAlarm{idx}",
                metric=latency_metric,
                threshold=constants.LATENCY_THRESHOLD_MS,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                alarm_description=f"Latency above {constants.LATENCY_THRESHOLD_MS} ms for {url}",
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
            )
            latency_alarm.add_alarm_action(cloudwatch_actions.SnsAction(alarm_topic))

            response_size_alarm = cloudwatch.Alarm(
                self,
                f"ResponseSizeZeroAlarm{idx}",
                metric=response_size_metric,
                threshold=constants.RESPONSE_SIZE_MIN_BYTES,
                comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                alarm_description=f"Response size is below {constants.RESPONSE_SIZE_MIN_BYTES} bytes for {url}",
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
            )
            response_size_alarm.add_alarm_action(cloudwatch_actions.SnsAction(alarm_topic))

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
            evaluation_periods=1,
            alarm_description="Lambda invocations below threshold - potential deployment issue",
            treat_missing_data=cloudwatch.TreatMissingData.BREACHING,
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
            threshold=0,
            evaluation_periods=1,
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
        deployment_group = codedeploy.LambdaDeploymentGroup(
            self,
            "BlueGreenDeployment",
            alias=alias,
            deployment_config=codedeploy.LambdaDeploymentConfig.CANARY_10_PERCENT_5_MINUTES,
            alarms=[invocations_alarm, duration_alarm, error_alarm, memory_alarm]
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
