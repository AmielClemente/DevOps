# Website Monitor Runbook

## Purpose
Operational steps to triage and resolve CloudWatch alarms for website availability and latency.

## Alarms
- AvailabilityAlarm-<url>: Fires when Availability < 0.99 for one period.
- LatencyAlarm-<url>: Fires when Latency > 500 ms for one period.
- Notifications go to SNS topic `WebsiteHealthAlertsTopic`.

## On-call Actions
1. Acknowledge alert from email/SNS endpoint.
2. Identify impacted URL from alarm name and open the CloudWatch Dashboard `WebsiteHealthDashboard`.
3. Correlate:
   - Check Lambda `WebsiteCrawlerLambda` logs (CloudWatch Logs) for HTTP status, exceptions, or timeouts.
   - Validate metric trends for other URLs to rule out systemic issues.

## Triage Steps
- Availability alarm:
  - Manually curl or browse the URL. Capture HTTP status and response time.
  - Check DNS/SSL certificate validity.
  - Contact website owner if the endpoint is external.
- Latency alarm:
  - Verify latency trend and p95.
  - Check from alternate network/location.
  - Look for throttling/timeouts in Lambda logs.

## Remediation
- If endpoint down: escalate to service owner; provide timestamps and observed status codes.
- If SSL/DNS issue: renew certificate or fix DNS records.
- If network slowness/regression: coordinate with provider; consider raising latency threshold temporarily after approval.

## Validation
- After remediation, confirm alarms return to OK.
- Spot-check metrics for 15 minutes.

## Runbook Maintenance
- Update thresholds or URLs in `website_monitor_cdk_stack.py` as needed.
- Ensure SNS subscribers are current. To add an email: set `ALERT_EMAIL` before deploy, or subscribe manually in the console. 