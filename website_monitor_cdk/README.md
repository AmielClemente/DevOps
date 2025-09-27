# Website Health Monitoring System

A comprehensive AWS-based website monitoring solution that continuously monitors website health and performance, providing real-time alerts and detailed analytics through CloudWatch dashboards.

## Features

### Core Monitoring
- **Automated Website Checks**: Monitors multiple websites every 5 minutes
- **Three Key Metrics**:
  - **Availability** — 1 if the site is up (HTTP 200), 0 if it's down
  - **Latency (ms)** — Response time measurement
  - **Response Size (bytes)** — Content size validation

### Alerting & Notifications
- **SNS Integration**: Real-time email notifications for critical issues
- **CloudWatch Alarms**: Three alarm types per monitored URL:
  - Availability < **99%** (site down)
  - Latency > **500 ms** (performance degradation)
  - Response Size < **1 byte** (empty page detection)

### Data Persistence & Logging
- **DynamoDB Table**: Stores alarm history and logs
- **Alarm Logger Lambda**: Automatically logs all alarm state changes
- **Comprehensive Logging**: Full audit trail of monitoring events

### Visualization
- **CloudWatch Dashboard**: Real-time graphs for all metrics
- **Multi-URL Support**: Monitor multiple websites simultaneously
- **Historical Data**: 6-hour rolling window with 1-minute granularity

## Architecture

The system consists of several AWS services working together in a serverless architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Application   │───▶│  Website Crawler │───▶│   CloudWatch    │
│   (Scheduled)   │    │     Lambda       │    │   (Metrics)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                │                        ▼
                                │              ┌─────────────────┐
                                │              │     ALARMS      │
                                │              │ (Thresholded    │
                                │              │  Metrics)       │
                                │              └─────────────────┘
                                │                        │
                                │                        ▼
                                │              ┌─────────────────┐
                                │              │   SNS Topic     │
                                │              │ (Notifications) │
                                │              └─────────────────┘
                                │                        │
                                │                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   DynamoDB      │◀───│  Alarm Logger   │
                       │   (Alarm Logs)  │    │     Lambda      │
                       └─────────────────┘    └─────────────────┘
```

### System Flow

1. **Website Crawler Lambda** (`wtlambda.py`):
   - Monitors websites every 5 minutes (triggered by EventBridge)
   - Publishes **latency**, **availability**, and **response size** metrics to CloudWatch
   - Handles HTTP requests and measures response times

2. **CloudWatch Monitoring Service**:
   - Receives and stores custom metrics from the Lambda function
   - Tracks metric values over time with 1-minute granularity
   - Provides historical data and trend analysis

3. **CloudWatch Alarms**:
   - Monitors thresholded metrics against predefined thresholds
   - Triggers when metrics breach thresholds (availability < 99%, latency > 500ms, response size < 1 byte)
   - Sends alarm state changes to SNS Topic via `add_alarm_action(SNS)`

4. **SNS Topic** (Notifications):
   - Receives alarm notifications from CloudWatch
   - Distributes alerts to email subscribers
   - Triggers Lambda subscription for alarm logging

5. **Alarm Logger Lambda** (`DBlambda.py`):
   - Subscribed to SNS Topic via `LambdaSubscription`
   - Processes alarm events with `lambda_handler(event, context)`
   - Logs alarm details to DynamoDB table

6. **DynamoDB Table**:
   - Stores alarm history and event logs
   - Provides persistent storage for alarm state changes
   - Enables historical analysis and audit trails

### AWS Services Used
- **Lambda Functions**: Website monitoring and alarm logging
- **EventBridge**: Scheduled execution (every 5 minutes)
- **CloudWatch**: Metrics, alarms, and dashboards
- **SNS**: Alert notifications via email
- **DynamoDB**: Alarm history storage
- **IAM**: Service permissions and access control

## Monitored Websites

Currently monitoring:
- `https://vuws.westernsydney.edu.au/`
- `https://westernsydney.edu.au/`
- `https://library.westernsydney.edu.au/`

## Configuration

### Alarm Thresholds
- **Availability**: < 99% triggers alarm
- **Latency**: > 500ms triggers alarm  
- **Response Size**: < 1 byte triggers alarm

### Monitoring Schedule
- **Frequency**: Every 5 minutes
- **Timeout**: 30 seconds per Lambda execution
- **Retry**: Automatic on failures

## Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Python 3.9+
- AWS CDK v2

### Installation & Deployment

```bash
# 1. Set up Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure AWS credentials
# Ensure your AWS CLI is configured with credentials that can deploy CloudFormation stacks
aws configure  # or use AWS SSO, environment variables, etc.

# 4. Deploy the stack
cd website_monitor_cdk
cdk bootstrap   # Only needed the first time in an account/region
cdk synth       # Generate CloudFormation template (sanity check)
cdk deploy      # Deploy the infrastructure
```

### Post-Deployment
1. **Check CloudWatch Dashboard**: Navigate to CloudWatch → Dashboards → "URL-MONITOR-DASHBOARD"
2. **Verify Alarms**: Check CloudWatch → Alarms for active monitoring
3. **Test Notifications**: Alarms will send emails to the configured address
4. **Review Logs**: Check DynamoDB table for alarm history

## 📈 Monitoring & Operations

### CloudWatch Dashboard
Access the dashboard at: CloudWatch → Dashboards → "URL-MONITOR-DASHBOARD"

**Dashboard Sections**:
- **Availability Graph**: Shows uptime percentage for all URLs
- **Latency Graph**: Displays response times in milliseconds
- **Response Size Graph**: Tracks content size in bytes

### Alarm Management
- **Alarm Names**: `AvailabilityAlarm{1-3}`, `LatencyAlarm{1-3}`, `ResponseSizeZeroAlarm{1-3}`
- **SNS Topic**: `WebsiteAlarmTopic` for all notifications
- **DynamoDB Table**: `WebsiteAlarmTable` for alarm logs

### Troubleshooting
1. **Check Lambda Logs**: CloudWatch Logs for execution details
2. **Verify Permissions**: Ensure IAM roles have required permissions
3. **Test URLs Manually**: Use curl or browser to verify site accessibility
4. **Review Alarm History**: Check DynamoDB table for alarm state changes

## Customization

### Adding New URLs
1. Edit `website_monitor_cdk/constants.py`
2. Add URL to the `URLS` list
3. Redeploy: `cdk deploy`

### Modifying Thresholds
1. Update values in `website_monitor_cdk/constants.py`:
   - `AVAIL_THRESHOLD`: Availability threshold (0.0-1.0)
   - `LATENCY_THRESHOLD_MS`: Latency threshold in milliseconds
   - `RESPONSE_SIZE_MIN_BYTES`: Minimum response size
2. Redeploy: `cdk deploy`

### Changing Alert Email
1. Update `ALERT_EMAIL` in `website_monitor_cdk/constants.py`
2. Redeploy: `cdk deploy`

## Requirements

- **Python**: 3.9+
- **AWS CDK**: v2.x
- **Dependencies**: See `requirements.txt`
- **AWS Permissions**: CloudFormation, Lambda, CloudWatch, SNS, DynamoDB, IAM

## Project Structure

```
website_monitor_cdk/
├── app.py                              # CDK app entry point
├── website_monitor_cdk_stack.py        # Main CDK stack definition
├── constants.py                        # Configuration constants
├── lambda/
│   ├── website_crawler/
│   │   └── lambda_function.py          # Website monitoring logic
│   └── alarm_logger/
│       └── alarm_logger.py             # Alarm logging logic
├── requirements.txt                    # Python dependencies
└── README.md                          # This file
```

## Operational Runbook

For detailed operational procedures, see `RUNBOOK.md` which includes:
- Alarm triage procedures
- Troubleshooting steps
- Remediation guidelines
- Maintenance tasks
