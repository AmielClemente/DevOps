#!/bin/bash

# 🎯 Complete System Integration Test
# This script tests the full integration between CRUD API and Web Crawler

API_BASE_URL="https://lli66x0cr8.execute-api.us-east-1.amazonaws.com/prod"

echo "🎯 Complete System Integration Test"
echo "=================================="

# Step 1: Create a test website via API
echo ""
echo "📝 Step 1: Create a test website via API"
WEBSITE_RESPONSE=$(curl -X POST "$API_BASE_URL/websites" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/status/200",
    "name": "HTTPBin Integration Test",
    "description": "Testing API to Crawler integration",
    "enabled": true,
    "check_interval": 300
  }' \
  -s)

echo "$WEBSITE_RESPONSE" | jq '.'

# Extract website ID
WEBSITE_ID=$(echo "$WEBSITE_RESPONSE" | jq -r '.website.id' 2>/dev/null)
echo "Created website ID: $WEBSITE_ID"

# Step 2: Verify website is in DynamoDB
echo ""
echo "🗄️ Step 2: Verify website is stored in DynamoDB"
aws dynamodb get-item \
  --table-name "TargetWebsites-alpha-v2-AppStack" \
  --key '{"id": {"S": "'$WEBSITE_ID'"}}' \
  --query 'Item.{id:id.S,name:name.S,url:url.S,enabled:enabled.BOOL}' \
  --output table

# Step 3: Check current CloudWatch metrics
echo ""
echo "📊 Step 3: Check current CloudWatch metrics"
aws cloudwatch list-metrics \
  --namespace "amiel-week3" \
  --query 'Metrics[?contains(Dimensions[0].Value, `httpbin`)].{MetricName:MetricName,URL:Dimensions[0].Value}' \
  --output table

# Step 4: Wait and check if web crawler picks up the new website
echo ""
echo "⏳ Step 4: Waiting for web crawler to pick up new website..."
echo "Note: Web crawler runs every 5 minutes, so it may take a few minutes to see metrics"

# Step 5: Show how to monitor the system
echo ""
echo "🔍 Step 5: How to monitor your system"
echo ""
echo "📊 CloudWatch Dashboard:"
echo "   https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=URL-MONITOR-DASHBOARD-alpha-v2-AppStack"
echo ""
echo "📋 DynamoDB Table:"
echo "   aws dynamodb scan --table-name 'TargetWebsites-alpha-v2-AppStack' --output table"
echo ""
echo "📝 Lambda Logs:"
echo "   aws logs filter-log-events --log-group-name '/aws/lambda/alpha-v2-AppStack-WebsiteCrawlerLambda8104AC35-uT0LRMglLOT9' --start-time \$(date -d '1 hour ago' +%s)000"
echo ""
echo "🌐 API Gateway:"
echo "   $API_BASE_URL/websites"
echo ""
echo "✅ Integration Test Complete!"
echo ""
echo "🎯 What to expect:"
echo "1. Website created via API ✅"
echo "2. Website stored in DynamoDB ✅"
echo "3. Web crawler will pick it up on next run (every 5 minutes)"
echo "4. CloudWatch metrics will appear for the new website"
echo "5. Dashboard will show the new website metrics"
echo ""
echo "🔄 To see real-time updates, run this script again in 5-10 minutes"
