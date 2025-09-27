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
    aws_dynamodb as dynamodb,
)
from constructs import Construct
import json
from datetime import datetime

# Import your constants (namespace, URLs, thresholds, etc.)
import constants


class WebsiteMonitorCdkStack(Stack):
    """
    This stack sets up:
      - A Lambda that checks our websites and publishes custom metrics
      - A schedule to run the Lambda every 5 minutes
      - A CloudWatch Dashboard with widgets for Availability, Latency, Response Size
      - Per-URL alarms that send notifications to SNS
      - A DynamoDB table for storing alarm logs
      - A Lambda that logs alarms from SNS into DynamoDB
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        
        # 1) Lambda for website monitoring
        website_crawler = _lambda.Function(
            self,
            "WebsiteCrawlerLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda/website_crawler"),
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

        
        # 2) SNS Topic for Alarms
        
        alarm_topic = sns.Topic(
            self,
            "WebsiteAlarmTopic",
            display_name="Website Monitoring Alarms"
        )

        # Human notification subscription
        if getattr(constants, "ALERT_EMAIL", None):
            alarm_topic.add_subscription(subs.EmailSubscription(constants.ALERT_EMAIL))

        
        # 3) DynamoDB Table for Alarm Logs
        
        alarm_table = dynamodb.Table(
            self,
            "WebsiteAlarmTable",
            partition_key=dynamodb.Attribute(name="AlarmName", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="Timestamp", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        
        # 4) Lambda for logging alarms
        alarm_logger = _lambda.Function(
            self,
            "AlarmLoggerLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="alarm_logger.lambda_handler",
            code=_lambda.Code.from_asset("lambda/alarm_logger"),
            environment={
                "ALARM_TABLE": alarm_table.table_name,
                "FORCE_UPDATE": str(datetime.utcnow())  #
            }
        )

        # Grant Lambda permissions to write to DynamoDB
        alarm_table.grant_write_data(alarm_logger)

        # Subscribe Lambda to SNS Topic
        alarm_topic.add_subscription(subs.LambdaSubscription(alarm_logger))

        
        # 5) CloudWatch Dashboard
        dashboard = cloudwatch.Dashboard(
            self,
            "Dashboard",
            dashboard_name="URL-MONITOR-DASHBOARD",
            start="-PT6H",
        )

        avail_series = []
        latency_series = []
        size_series = []

        # Create metrics, alarms per URL
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
