import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table_name = os.environ["ALARM_TABLE"]
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    # Handle direct test events or malformed payloads gracefully
    records = event.get("Records")
    processed = 0

    if not records:
        # Support direct CloudWatch Alarm message (not via SNS) for testing
        if all(k in event for k in ("AlarmName", "NewStateValue", "NewStateReason")):
            table.put_item(
                Item={
                    "AlarmName": event["AlarmName"],
                    "Timestamp": datetime.utcnow().isoformat(),
                    "State": event["NewStateValue"],
                    "Reason": event["NewStateReason"],
                }
            )
            processed = 1
        else:
            # Nothing to do
            return {"statusCode": 200, "body": "No Records; nothing processed"}

    else:
        for record in records:
            sns_obj = record.get("Sns") or record.get("SNS")
            if not sns_obj:
                continue

            raw_message = sns_obj.get("Message")
            if raw_message is None:
                continue

            # Parse message which can be a JSON string or already a dict
            if isinstance(raw_message, str):
                try:
                    message = json.loads(raw_message)
                except json.JSONDecodeError:
                    # If not JSON, store as raw reason
                    message = {"AlarmName": "UNKNOWN", "NewStateValue": "UNKNOWN", "NewStateReason": raw_message}
            elif isinstance(raw_message, dict):
                message = raw_message
            else:
                continue

            alarm_name = message.get("AlarmName")
            state = message.get("NewStateValue")
            reason = message.get("NewStateReason")

            # Require keys for the PK/SK
            if not alarm_name:
                continue

            table.put_item(
                Item={
                    "AlarmName": alarm_name,
                    "Timestamp": datetime.utcnow().isoformat(),
                    "State": state or "UNKNOWN",
                    "Reason": reason or "",
                }
            )
            processed += 1

    return {"statusCode": 200, "body": f"Processed {processed} record(s)"}
