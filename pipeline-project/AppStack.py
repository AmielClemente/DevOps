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

        # 1) Website Crawler Lambda
        wh_lambda = self.create_website_crawler_lambda()

        # 2) Alarm Logger Lambda  
        db_lambda = self.create_alarm_logger_lambda()

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

    def create_website_crawler_lambda(self):
        """Create the website crawler Lambda function"""
        website_crawler = _lambda.Function(
            self,
            "WebsiteCrawlerLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("website_monitor_cdk/lambda/website_crawler"),
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

    def create_alarm_logger_lambda(self):
        """Create the alarm logger Lambda function"""
        alarm_logger = _lambda.Function(
            self,
            "AlarmLoggerLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="alarm_logger.lambda_handler",
            code=_lambda.Code.from_asset("website_monitor_cdk/lambda/alarm_logger"),
            environment={
                "ALARM_TABLE": "WebsiteAlarmTable",  # Will be set by DatabaseStack
                "FORCE_UPDATE": str(datetime.utcnow())
            }
        )

        return alarm_logger

    def create_dashboard(self):
        """Create CloudWatch Dashboard"""
        dashboard = cloudwatch.Dashboard(
            self,
            "Dashboard",
            dashboard_name="URL-MONITOR-DASHBOARD",
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
