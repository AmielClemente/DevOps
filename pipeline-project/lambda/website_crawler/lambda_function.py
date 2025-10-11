import boto3
import urllib.request
import urllib.error
import time
import json
import os
import logging
from boto3.dynamodb.conditions import Attr

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Website monitoring Lambda function using built-in libraries
    cw = boto3.client("cloudwatch")
    dynamodb = boto3.resource("dynamodb")
    
    # Get table name from environment variable
    table_name = os.environ.get("TARGET_WEBSITES_TABLE")
    if not table_name:
        logger.error("TARGET_WEBSITES_TABLE environment variable not set")
        return {"statusCode": 500, "body": "Configuration error"}
    
    table = dynamodb.Table(table_name)
    
    # Get configuration from environment variables
    namespace = os.environ.get("NAMESPACE", "amiel-week3")
    availability_metric = os.environ.get("AVAILABILITY_METRIC_NAME", "Availability")
    latency_metric = os.environ.get("LATENCY_METRIC_NAME", "Latency")
    response_size_metric = os.environ.get("RESPONSE_SIZE_METRIC_NAME", "ResponseSize")

    logger.info(f"Starting website monitoring")
    
    try:
        # Get enabled websites from DynamoDB
        response = table.scan(
            FilterExpression=Attr('enabled').eq(True)
        )
        urls = [item['url'] for item in response.get('Items', [])]
        
        if not urls:
            logger.warning("No enabled websites found in target list")
            return {"statusCode": 200, "body": "No websites to monitor"}
        
        logger.info(f"Found {len(urls)} enabled websites to monitor")
        
    except Exception as e:
        logger.error(f"Error reading from DynamoDB: {str(e)}")
        return {"statusCode": 500, "body": "Database error"}
    
    successful_checks = 0
    failed_checks = 0

    for url in urls:
        start = time.time()
        try:
            # Use urllib instead of requests to avoid external dependencies
            with urllib.request.urlopen(url, timeout=5) as response:
                latency_ms = (time.time() - start) * 1000.0
                availability = 1 if response.status == 200 else 0
                size = len(response.read())
                successful_checks += 1
                logger.info(f"Successfully checked {url}: {response.status}, {latency_ms:.2f}ms")
        except urllib.error.HTTPError as e:
            # HTTP errors (4xx, 5xx) - log but don't fail
            latency_ms = (time.time() - start) * 1000.0
            availability = 0
            size = 0
            failed_checks += 1
            logger.warning(f"HTTP error for {url}: {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            # Network errors - log but don't fail
            latency_ms = 0
            availability = 0
            size = 0
            failed_checks += 1
            logger.warning(f"URL error for {url}: {e.reason}")
        except Exception as e:
            # Other errors - log but don't fail
            latency_ms = 0
            availability = 0
            size = 0
            failed_checks += 1
            logger.error(f"Unexpected error for {url}: {str(e)}")

        try:
            cw.put_metric_data(
                Namespace=namespace,
                MetricData=[
                    {
                        "MetricName": availability_metric,
                        "Dimensions": [{"Name": "URL", "Value": url}],
                        "Value": availability,
                    },
                    {
                        "MetricName": latency_metric,
                        "Dimensions": [{"Name": "URL", "Value": url}],
                        "Value": latency_ms,
                    },
                    {
                        "MetricName": response_size_metric,
                        "Dimensions": [{"Name": "URL", "Value": url}],
                        "Value": size,
                    },
                ],
            )
        except Exception as e:
            logger.error(f"Failed to put metric data for {url}: {str(e)}")
            # Don't fail the entire function for metric publishing errors

    logger.info(f"Monitoring complete: {successful_checks} successful, {failed_checks} failed")
    return {"statusCode": 200, "body": f"Checked {len(urls)} URLs: {successful_checks} successful, {failed_checks} failed"}
