# 🧪 CRUD API Testing Guide

## Overview

This guide shows you how to test the Website Crawler CRUD API system. The API provides RESTful endpoints for managing target websites stored in DynamoDB.

## Testing Methods

### **1. Local Unit Testing**

Run the comprehensive test suite locally:

```bash
# Install dependencies
pip install pytest boto3 moto

# Run all CRUD API tests
python -m pytest tests/test_crud_api.py -v

# Run specific test categories
python -m pytest tests/test_crud_api.py::TestCRUDAPI::test_create_website_success -v
python -m pytest tests/test_crud_api.py::TestCRUDAPI::test_dynamodb_performance_read -v
```

### **2. Manual API Testing with curl**

Once deployed, test the API endpoints directly:

#### **Get API Gateway URL**
```bash
# Find your API Gateway URL
aws apigateway get-rest-apis --query 'items[?name==`Website Target CRUD API`].{Id:id,Name:name}' --output table

# Get the full URL (replace {api-id} and {region})
API_URL="https://{api-id}.execute-api.{region}.amazonaws.com/prod"
```

#### **Test CRUD Operations**

**1. Create a new website:**
```bash
curl -X POST $API_URL/websites \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "name": "Example Website",
    "description": "A test website",
    "enabled": true,
    "check_interval": 300
  }'
```

**2. List all websites:**
```bash
curl -X GET $API_URL/websites
```

**3. Get specific website (replace {id} with actual ID):**
```bash
curl -X GET $API_URL/websites/{id}
```

**4. Update website:**
```bash
curl -X PUT $API_URL/websites/{id} \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Website Name",
    "enabled": false
  }'
```

**5. Delete website:**
```bash
curl -X DELETE $API_URL/websites/{id}
```

### **3. Python Script Testing**

Create a test script to interact with the API:

```python
import requests
import json

# Replace with your actual API Gateway URL
API_BASE_URL = "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod"

def test_crud_operations():
    """Test all CRUD operations"""
    
    # 1. Create a website
    create_data = {
        "url": "https://httpbin.org/status/200",
        "name": "HTTPBin Test",
        "description": "Testing website",
        "enabled": True,
        "check_interval": 300
    }
    
    print("1. Creating website...")
    response = requests.post(f"{API_BASE_URL}/websites", json=create_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        website_id = response.json()['website']['id']
        print(f"Created website with ID: {website_id}")
        
        # 2. Get the website
        print("\n2. Getting website...")
        response = requests.get(f"{API_BASE_URL}/websites/{website_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 3. Update the website
        print("\n3. Updating website...")
        update_data = {
            "name": "Updated HTTPBin Test",
            "enabled": False
        }
        response = requests.put(f"{API_BASE_URL}/websites/{website_id}", json=update_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 4. List all websites
        print("\n4. Listing all websites...")
        response = requests.get(f"{API_BASE_URL}/websites")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 5. Delete the website
        print("\n5. Deleting website...")
        response = requests.delete(f"{API_BASE_URL}/websites/{website_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_crud_operations()
```

### **4. DynamoDB Direct Testing**

Test the DynamoDB table directly:

```bash
# List DynamoDB tables
aws dynamodb list-tables --query 'TableNames[?contains(@, `TargetWebsites`)]'

# Get table details
aws dynamodb describe-table --table-name TargetWebsites-{stack-name}

# Scan table contents
aws dynamodb scan --table-name TargetWebsites-{stack-name}

# Put item directly
aws dynamodb put-item \
  --table-name TargetWebsites-{stack-name} \
  --item '{
    "id": {"S": "test-id-123"},
    "url": {"S": "https://example.com"},
    "name": {"S": "Test Website"},
    "enabled": {"BOOL": true},
    "created_at": {"S": "2024-01-01T00:00:00.000Z"},
    "updated_at": {"S": "2024-01-01T00:00:00.000Z"}
  }'
```

### **5. Lambda Function Testing**

Test the Lambda function directly:

```bash
# List Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `CRUD`)].{Name:FunctionName,Runtime:Runtime}'

# Test Lambda function with sample event
aws lambda invoke \
  --function-name {crud-lambda-name} \
  --payload '{
    "httpMethod": "GET",
    "pathParameters": null,
    "body": null
  }' \
  response.json

cat response.json
```

## Expected Test Results

### **Successful API Responses**

**Create Website (POST):**
```json
{
  "message": "Website created successfully",
  "website": {
    "id": "uuid-string",
    "url": "https://example.com",
    "name": "Example Website",
    "description": "A test website",
    "enabled": true,
    "created_at": "2024-01-01T00:00:00.000Z",
    "updated_at": "2024-01-01T00:00:00.000Z"
  }
}
```

**List Websites (GET):**
```json
{
  "websites": [...],
  "count": 1
}
```

**Get Website (GET):**
```json
{
  "website": {
    "id": "uuid-string",
    "url": "https://example.com",
    "name": "Example Website",
    ...
  }
}
```

### **Error Responses**

**Missing URL (400):**
```json
{
  "error": "URL is required"
}
```

**Website Not Found (404):**
```json
{
  "error": "Website not found"
}
```

## Performance Testing

### **DynamoDB Performance Benchmarks**

- **Read Operations**: Should complete within 100ms
- **Write Operations**: Should complete within 200ms
- **Scan Operations**: Varies by table size

### **API Gateway Performance**

- **Cold Start**: First request may take 1-2 seconds
- **Warm Requests**: Should complete within 500ms
- **Concurrent Requests**: Test with multiple simultaneous requests

## Troubleshooting

### **Common Issues**

1. **API Gateway Not Found**
   - Check if the stack deployed successfully
   - Verify API Gateway was created
   - Check CloudFormation events for errors

2. **Lambda Function Errors**
   - Check Lambda function logs in CloudWatch
   - Verify DynamoDB permissions
   - Check environment variables

3. **DynamoDB Access Issues**
   - Verify IAM permissions
   - Check table name and region
   - Ensure table exists

4. **CORS Issues**
   - Check API Gateway CORS configuration
   - Verify preflight requests are handled

### **Debugging Commands**

```bash
# Check CloudFormation stack status
aws cloudformation describe-stacks --stack-name PipelineProjectStackV2

# Check Lambda function logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/

# Check API Gateway logs
aws logs describe-log-groups --log-group-name-prefix API-Gateway-Execution-Logs

# Test API Gateway directly
aws apigateway test-invoke-method \
  --rest-api-id {api-id} \
  --resource-id {resource-id} \
  --http-method GET
```

## Integration with Web Crawler

### **Testing Integration**

1. **Create websites via API**
2. **Verify they appear in crawler configuration**
3. **Check monitoring starts automatically**
4. **Verify alarms are triggered correctly**

### **End-to-End Testing**

```bash
# 1. Create a test website
curl -X POST $API_URL/websites -H "Content-Type: application/json" -d '{
  "url": "https://httpbin.org/status/200",
  "name": "Test Site",
  "enabled": true
}'

# 2. Wait for crawler to pick it up (check CloudWatch logs)
aws logs filter-log-events \
  --log-group-name /aws/lambda/{crawler-function-name} \
  --start-time $(date -d '5 minutes ago' +%s)000

# 3. Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace "URL-MONITOR" \
  --metric-name "Availability" \
  --dimensions Name=URL,Value=https://httpbin.org/status/200 \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Average
```

## Next Steps

1. **Deploy the infrastructure** if not already done
2. **Get the API Gateway URL** from AWS Console or CLI
3. **Run the tests** using the methods above
4. **Verify integration** with the web crawler
5. **Monitor performance** and adjust as needed

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review CloudFormation events for deployment errors
3. Check Lambda function logs in CloudWatch
4. Verify IAM permissions and resource configurations
