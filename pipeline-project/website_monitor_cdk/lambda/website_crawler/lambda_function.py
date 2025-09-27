import boto3
import requests
import time
import json
import os

def lambda_handler(event, context):
    cw = boto3.client("cloudwatch")
    
    # Get URLs from environment variable (set by CDK)
    urls = json.loads(os.environ.get("URLS", "[]"))
    namespace = os.environ.get("NAMESPACE", "amiel-week3")
    availability_metric = os.environ.get("AVAILABILITY_METRIC_NAME", "Availability")
    latency_metric = os.environ.get("LATENCY_METRIC_NAME", "Latency")
    response_size_metric = os.environ.get("RESPONSE_SIZE_METRIC_NAME", "ResponseSize")

    for url in urls:
        start = time.time()
        try:
            resp = requests.get(url, timeout=5)
            latency_ms = (time.time() - start) * 1000.0
            availability = 1 if resp.status_code == 200 else 0
            size = len(resp.content)
        except Exception:
            latency_ms = 0
            availability = 0
            size = 0

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

    return {"statusCode": 200, "body": f"Checked {len(urls)} URLs"}