import boto3
import requests
import time

# Websites to check
URLS = [
    "https://vuws.westernsydney.edu.au/",
    "https://westernsydney.edu.au/",
    "https://library.westernsydney.edu.au/",
]

# Custom metrics namespace + names (must match CDK/constants)
URL_NAMESPACE = "amiel-week3"
URL_MONITOR_AVAILABILITY = "Availability"
URL_MONITOR_LATENCY = "Latency"
URL_MONITOR_RESPONSE_SIZE = "ResponseSize"

def lambda_handler(event, context):
    cw = boto3.client("cloudwatch")

    for url in URLS:
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
            Namespace=URL_NAMESPACE,
            MetricData=[
                {
                    "MetricName": URL_MONITOR_AVAILABILITY,
                    "Dimensions": [{"Name": "URL", "Value": url}],
                    "Value": availability,
                },
                {
                    "MetricName": URL_MONITOR_LATENCY,
                    "Dimensions": [{"Name": "URL", "Value": url}],
                    "Value": latency_ms,
                },
                {
                    "MetricName": URL_MONITOR_RESPONSE_SIZE,
                    "Dimensions": [{"Name": "URL", "Value": url}],
                    "Value": size,
                },
            ],
        )

    return {"statusCode": 200, "body": f"Checked {len(URLS)} URLs"}
