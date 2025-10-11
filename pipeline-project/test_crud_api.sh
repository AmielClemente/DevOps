#!/bin/bash

# 🧪 CRUD API Testing Script
# This script tests all CRUD operations on your Website Target API

# Set your API Gateway URL (replace with your actual URL)
API_BASE_URL="https://lli66x0cr8.execute-api.us-east-1.amazonaws.com/prod"

echo "🚀 Testing Website Target CRUD API"
echo "API URL: $API_BASE_URL"
echo "=================================="

# Test 1: List all websites (should be empty initially)
echo ""
echo "📋 Test 1: List all websites"
echo "GET $API_BASE_URL/websites"
curl -X GET "$API_BASE_URL/websites" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.' 2>/dev/null || echo "Response received"

# Test 2: Create a new website
echo ""
echo "➕ Test 2: Create a new website"
echo "POST $API_BASE_URL/websites"
WEBSITE_RESPONSE=$(curl -X POST "$API_BASE_URL/websites" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/status/200",
    "name": "HTTPBin Test Site",
    "description": "A test website for monitoring",
    "enabled": true,
    "check_interval": 300,
    "timeout": 30,
    "expected_status": 200
  }' \
  -w "\nHTTP Status: %{http_code}\n" \
  -s)

echo "$WEBSITE_RESPONSE"

# Extract website ID from response
WEBSITE_ID=$(echo "$WEBSITE_RESPONSE" | jq -r '.website.id' 2>/dev/null)
echo "Created website ID: $WEBSITE_ID"

# Test 3: Get the specific website
if [ "$WEBSITE_ID" != "null" ] && [ "$WEBSITE_ID" != "" ]; then
  echo ""
  echo "🔍 Test 3: Get specific website"
  echo "GET $API_BASE_URL/websites/$WEBSITE_ID"
  curl -X GET "$API_BASE_URL/websites/$WEBSITE_ID" \
    -H "Content-Type: application/json" \
    -w "\nHTTP Status: %{http_code}\n" \
    -s | jq '.' 2>/dev/null || echo "Response received"
fi

# Test 4: Update the website
if [ "$WEBSITE_ID" != "null" ] && [ "$WEBSITE_ID" != "" ]; then
  echo ""
  echo "✏️ Test 4: Update website"
  echo "PUT $API_BASE_URL/websites/$WEBSITE_ID"
  curl -X PUT "$API_BASE_URL/websites/$WEBSITE_ID" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Updated HTTPBin Test Site",
      "description": "Updated description",
      "enabled": false
    }' \
    -w "\nHTTP Status: %{http_code}\n" \
    -s | jq '.' 2>/dev/null || echo "Response received"
fi

# Test 5: List websites again (should show the created website)
echo ""
echo "📋 Test 5: List websites again"
echo "GET $API_BASE_URL/websites"
curl -X GET "$API_BASE_URL/websites" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.' 2>/dev/null || echo "Response received"

# Test 6: Create another website for monitoring
echo ""
echo "➕ Test 6: Create another website"
echo "POST $API_BASE_URL/websites"
curl -X POST "$API_BASE_URL/websites" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "name": "Example Website",
    "description": "Another test website",
    "enabled": true,
    "check_interval": 300
  }' \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.' 2>/dev/null || echo "Response received"

# Test 7: Test error handling - invalid URL
echo ""
echo "❌ Test 7: Test error handling - invalid URL"
echo "POST $API_BASE_URL/websites"
curl -X POST "$API_BASE_URL/websites" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "invalid-url",
    "name": "Invalid Website"
  }' \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.' 2>/dev/null || echo "Response received"

# Test 8: Test error handling - missing required fields
echo ""
echo "❌ Test 8: Test error handling - missing required fields"
echo "POST $API_BASE_URL/websites"
curl -X POST "$API_BASE_URL/websites" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Missing URL Website"
  }' \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.' 2>/dev/null || echo "Response received"

# Test 9: Test CORS headers
echo ""
echo "🌐 Test 9: Test CORS headers"
echo "OPTIONS $API_BASE_URL/websites"
curl -X OPTIONS "$API_BASE_URL/websites" \
  -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -w "\nHTTP Status: %{http_code}\n" \
  -v 2>&1 | grep -E "(Access-Control|HTTP/)"

# Test 10: Final list to see all websites
echo ""
echo "📋 Test 10: Final list of all websites"
echo "GET $API_BASE_URL/websites"
curl -X GET "$API_BASE_URL/websites" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.' 2>/dev/null || echo "Response received"

echo ""
echo "✅ CRUD API Testing Complete!"
echo ""
echo "🔍 Next Steps:"
echo "1. Check CloudWatch logs for the web crawler Lambda function"
echo "2. Verify that websites are being monitored (check CloudWatch metrics)"
echo "3. Test the CloudWatch dashboard"
echo "4. Check DynamoDB table for stored websites"
echo ""
echo "📊 Monitor your system:"
echo "- CloudWatch Dashboard: Look for 'URL-MONITOR-DASHBOARD'"
echo "- DynamoDB Table: Check 'TargetWebsitesTable'"
echo "- Lambda Logs: Check '/aws/lambda/WebsiteCrawlerLambda' logs"
echo "- API Gateway Logs: Check API Gateway execution logs"
