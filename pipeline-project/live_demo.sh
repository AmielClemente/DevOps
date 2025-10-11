#!/bin/bash

# 🎯 Project 2 Live Demo Script
# Run this during your presentation to demonstrate Project 2

API_URL="https://lli66x0cr8.execute-api.us-east-1.amazonaws.com/prod"

echo "🎯 PROJECT 2 LIVE DEMO"
echo "====================="
echo ""
echo "Project 2: CRUD API Gateway for Website Monitoring"
echo "This extends Project 1 with a public REST API for managing websites"
echo ""

# Demo 1: Show current websites
echo "📋 DEMO 1: List all currently monitored websites"
echo "GET $API_URL/websites"
echo ""
curl -X GET "$API_URL/websites" | jq '.websites[] | {name: .name, url: .url, enabled: .enabled}'
echo ""

# Demo 2: Add new website
echo "➕ DEMO 2: Add a new website to monitor"
echo "POST $API_URL/websites"
echo ""
NEW_WEBSITE=$(curl -s -X POST "$API_URL/websites" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/status/200",
    "name": "Presentation Demo Site",
    "description": "Added during live demo",
    "enabled": true,
    "check_interval": 300,
    "timeout": 30,
    "expected_status": 200
  }')

echo "$NEW_WEBSITE" | jq '.website | {id: .id, name: .name, url: .url, enabled: .enabled}'

# Extract ID for next demos
DEMO_ID=$(echo "$NEW_WEBSITE" | jq -r '.website.id')
echo ""

# Demo 3: Get specific website
echo "🔍 DEMO 3: Get details of the website we just created"
echo "GET $API_URL/websites/$DEMO_ID"
echo ""
curl -X GET "$API_URL/websites/$DEMO_ID" | jq '.website | {id: .id, name: .name, url: .url, enabled: .enabled, check_interval: .check_interval}'
echo ""

# Demo 4: Update website
echo "✏️ DEMO 4: Update the website settings"
echo "PUT $API_URL/websites/$DEMO_ID"
echo ""
curl -X PUT "$API_URL/websites/$DEMO_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Demo Site",
    "enabled": false,
    "check_interval": 600,
    "timeout": 60
  }' | jq '.website | {id: .id, name: .name, url: .url, enabled: .enabled, check_interval: .check_interval}'
echo ""

# Demo 5: Show error handling
echo "⚠️ DEMO 5: Show error handling with invalid data"
echo "POST $API_URL/websites (with invalid URL)"
echo ""
curl -X POST "$API_URL/websites" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "invalid-url",
    "name": "Invalid Website"
  }' | jq '.'
echo ""

# Demo 6: Delete website
echo "🗑️ DEMO 6: Remove the demo website"
echo "DELETE $API_URL/websites/$DEMO_ID"
echo ""
curl -X DELETE "$API_URL/websites/$DEMO_ID" | jq '.'
echo ""

echo "✅ DEMO COMPLETE!"
echo ""
echo "🎯 What we demonstrated:"
echo "1. ✅ List all websites (GET /websites)"
echo "2. ✅ Create new website (POST /websites)"
echo "3. ✅ Get specific website (GET /websites/{id})"
echo "4. ✅ Update website settings (PUT /websites/{id})"
echo "5. ✅ Error handling and validation"
echo "6. ✅ Delete website (DELETE /websites/{id})"
echo ""
echo "🔗 Integration with Project 1:"
echo "- Websites are stored in DynamoDB"
echo "- Web crawler reads from DynamoDB every 5 minutes"
echo "- CloudWatch metrics generated for monitored sites"
echo ""
echo "📊 Production Features:"
echo "- CORS support for web applications"
echo "- Comprehensive error handling"
echo "- Input validation and sanitization"
echo "- Audit logging via CloudWatch"
echo "- Pay-per-request billing model"
echo ""
echo "🎉 Project 2 is production-ready!"
