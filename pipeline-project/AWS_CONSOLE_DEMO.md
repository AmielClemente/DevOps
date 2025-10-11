# 🎯 AWS Console Demo Guide for Project 2

## 🌐 **Direct AWS Console Links**

### **1. API Gateway Console**
**URL:** https://console.aws.amazon.com/apigateway/home?region=us-east-1#/apis

**What to Show:**
- **API Name:** `Website Target CRUD API`
- **API ID:** `lli66x0cr8`
- **Resources:** `/websites` and `/websites/{id}`
- **Methods:** GET, POST, PUT, DELETE, OPTIONS
- **Integration:** Lambda function integration
- **CORS:** Enabled for all origins

**Demo Steps:**
1. Navigate to API Gateway console
2. Click on "Website Target CRUD API"
3. Show the `/websites` resource
4. Click on any method (e.g., GET)
5. Show the Lambda integration
6. Click "Test" to test the API directly

### **2. Lambda Functions Console**
**URL:** https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions

**What to Show:**
- **CRUD Lambda:** `alpha-v2-AppStack-CRUDLambdaAA054AF0-T6O3NgEjOvVR`
- **Web Crawler Lambda:** `alpha-v2-AppStack-WebsiteCrawlerLambda8104AC35-uT0LRMglLOT9`

**Demo Steps:**
1. Navigate to Lambda console
2. Click on the CRUD Lambda function
3. Show the function code
4. Show environment variables
5. Show the DynamoDB permissions
6. Click "Test" to test the function

### **3. DynamoDB Console**
**URL:** https://console.aws.amazon.com/dynamodb/home?region=us-east-1#tables:

**What to Show:**
- **Table Name:** `TargetWebsites-alpha-v2-AppStack`
- **Items:** All website entries
- **Schema:** id (partition key), enabled-index (GSI)

**Demo Steps:**
1. Navigate to DynamoDB console
2. Click on `TargetWebsites-alpha-v2-AppStack`
3. Click "Items" tab
4. Show the website entries
5. Click on any item to see details
6. Show the GSI (enabled-index)

### **4. CloudWatch Console**
**URL:** https://console.aws.amazon.com/cloudwatch/home?region=us-east-1

**What to Show:**
- **Logs:** Lambda function logs
- **Metrics:** API Gateway and Lambda metrics
- **Dashboards:** Website monitoring dashboard

**Demo Steps:**
1. Navigate to CloudWatch console
2. Click "Logs" → "Log groups"
3. Find the CRUD Lambda log group
4. Show recent log entries
5. Click "Metrics" to show API Gateway metrics

## 🎯 **Live Demo Script for AWS Console**

### **Step 1: API Gateway Demo**
```
1. Go to API Gateway console
2. Click "Website Target CRUD API"
3. Click "/websites" resource
4. Click "GET" method
5. Click "TEST" button
6. Click "Test" to execute
7. Show the JSON response
```

### **Step 2: DynamoDB Demo**
```
1. Go to DynamoDB console
2. Click "TargetWebsites-alpha-v2-AppStack"
3. Click "Items" tab
4. Show the website entries
5. Click on any item to see details
6. Show the enabled-index GSI
```

### **Step 3: Lambda Demo**
```
1. Go to Lambda console
2. Click on CRUD Lambda function
3. Show the function code
4. Show environment variables
5. Show the DynamoDB permissions
6. Click "Test" to test the function
```

### **Step 4: CloudWatch Demo**
```
1. Go to CloudWatch console
2. Click "Logs" → "Log groups"
3. Find CRUD Lambda log group
4. Show recent log entries
5. Click "Metrics" to show API Gateway metrics
```

## 🚀 **Presentation Flow**

### **Opening (1 minute):**
- "Let me show you Project 2 in the AWS Console"
- "We'll see the API Gateway, Lambda functions, and DynamoDB table"
- "This demonstrates the complete architecture"

### **API Gateway Demo (2 minutes):**
- Show the API structure
- Test the GET method directly
- Show the Lambda integration
- Explain CORS configuration

### **DynamoDB Demo (1 minute):**
- Show the table structure
- Display website entries
- Show the GSI for enabled websites
- Explain the schema

### **Lambda Demo (1 minute):**
- Show the CRUD function code
- Show environment variables
- Show DynamoDB permissions
- Test the function

### **CloudWatch Demo (1 minute):**
- Show function logs
- Show API Gateway metrics
- Show monitoring capabilities

### **Closing (30 seconds):**
- "This shows the complete Project 2 architecture"
- "All components are working together"
- "The system is production-ready"

## 📊 **Key Metrics to Show**

### **API Gateway Metrics:**
- **4XX Errors:** Should be low
- **5XX Errors:** Should be very low
- **Latency:** Should be < 200ms
- **Count:** Number of API calls

### **Lambda Metrics:**
- **Invocations:** Number of function calls
- **Duration:** Execution time
- **Errors:** Function errors
- **Throttles:** Function throttling

### **DynamoDB Metrics:**
- **Consumed Read Capacity:** Read operations
- **Consumed Write Capacity:** Write operations
- **Throttled Requests:** Throttling events

## 🎯 **Pro Tips for Demo**

### **1. Prepare Beforehand:**
- Open all AWS console tabs
- Have the demo data ready
- Test the API calls beforehand

### **2. Show Real Data:**
- Use actual website entries
- Show real API responses
- Display actual metrics

### **3. Explain Architecture:**
- Show how components connect
- Explain the data flow
- Highlight scalability features

### **4. Demonstrate Integration:**
- Show how API Gateway calls Lambda
- Show how Lambda writes to DynamoDB
- Show how web crawler reads from DynamoDB

## 🎉 **Summary**

**Yes, Project 2 can be fully demonstrated in the AWS Console!**

- ✅ **API Gateway:** Show API structure and test methods
- ✅ **Lambda:** Show function code and test execution
- ✅ **DynamoDB:** Show table data and schema
- ✅ **CloudWatch:** Show logs and metrics
- ✅ **Integration:** Show how all components work together

This makes your presentation even more impressive by showing the **real AWS infrastructure** behind Project 2!
