# Namespace and metric names must match what your Lambda publishes
URL_MONITOR_NAMESPACE = "amiel-week3"
AVAILABILITY_METRIC_NAME = "Availability"
LATENCY_METRIC_NAME = "Latency"
RESPONSE_SIZE_METRIC_NAME = "ResponseSize"
ALERT_EMAIL = "22070210@student.westernsydney.edu.au"

# URLs to monitor 
URLS = [
    "https://vuws.westernsydney.edu.au/",
    "https://westernsydney.edu.au/"
    "https://library.westernsydney.edu.au/",
]

# Alarm thresholds
AVAIL_THRESHOLD = 0.99
LATENCY_THRESHOLD_MS = 500
RESPONSE_SIZE_MIN_BYTES = 1
