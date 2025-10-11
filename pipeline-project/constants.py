# Namespace and metric names must match what your Lambda publishes
URL_MONITOR_NAMESPACE = "amiel-week3"
AVAILABILITY_METRIC_NAME = "Availability"
LATENCY_METRIC_NAME = "Latency"
RESPONSE_SIZE_METRIC_NAME = "ResponseSize"
ALERT_EMAIL = "22070210@student.westernsydney.edu.au"

# URLs are now managed dynamically via DynamoDB and CRUD API
# No hardcoded URLs - everything is managed through the REST API

# Alarm thresholds
AVAIL_THRESHOLD = 0.99
LATENCY_THRESHOLD_MS = 500
RESPONSE_SIZE_MIN_BYTES = 1
