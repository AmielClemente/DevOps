# 🚀 Website Monitoring CI/CD Pipeline with CRUD API

A comprehensive CI/CD pipeline built with AWS CodePipeline and CDK that automatically builds, tests, and deploys the Website Monitoring Application with a public CRUD API for managing target websites across multiple environments.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│     GitHub      │───▶│   CodePipeline   │───▶│   CodeBuild     │
│   (Source)      │    │   (Orchestrator) │    │   (Build/Test)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                │                        ▼
                                │              ┌─────────────────┐
                                │              │  CloudFormation │
                                │              │   (Deploy)      │
                                │              └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Beta Stage    │    │  Gamma Stage    │
                       │  (Testing)      │    │  (Staging)      │
                       └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │Production Stage │
                                              │  (Live)         │
                                              └─────────────────┘
```

## 🌐 Application Components

### **Website Monitoring System**
- **Lambda Functions**: Website crawler and alarm logger
- **DynamoDB Tables**: Alarm logging and target websites storage
- **CloudWatch**: Monitoring, alarms, and dashboards
- **SNS**: Alert notifications
- **CodeDeploy**: Blue-green deployments

### **CRUD API System** ✅
- **API Gateway**: RESTful endpoints for website management
- **CRUD Lambda**: Handles Create, Read, Update, Delete operations
- **DynamoDB**: Stores target websites configuration
- **CORS Support**: Cross-origin resource sharing enabled
- **Real-time Integration**: Web crawler automatically reads from API-managed database

## 🎯 Pipeline Stages

### **1. Source Stage**
- **Trigger**: GitHub webhook on push to main branch
- **Action**: Pulls latest code from repository
- **Output**: Source code artifacts

### **2. Build Stage**
- **Environment**: AWS CodeBuild with Python 3.9
- **Actions**:
  - Install dependencies (CDK, boto3, pytest)
  - Run unit tests
  - Synthesize CloudFormation templates
  - Package artifacts
- **Output**: Built application artifacts

### **3. Deploy Stages**
- **Alpha**: Development/testing environment (Unit Tests)
- **Beta**: Staging environment (Functional Tests)
- **Gamma**: Pre-production environment (Integration Tests)
- **Production**: Live environment (Infrastructure Tests) 

## 🔧 Prerequisites

### **AWS Setup**
1. **AWS CLI configured** with appropriate permissions
2. **CDK Bootstrap** completed in your account/region
3. **GitHub Token** stored in AWS Systems Manager Parameter Store

### **GitHub Setup**
1. **Repository** with your website monitoring code
2. **Personal Access Token** with repo access
3. **Webhook** configured (optional, for automatic triggers)

## 🚀 Quick Start

### **1. Store GitHub Token**
```bash
aws ssm put-parameter \
  --name "/github/token" \
  --value "your-github-token" \
  --type "SecureString"
```

### **2. Update Configuration**
Edit `pipeline_project_stack.py` and update:
- GitHub username: `owner="your-github-username"`
- Repository name: `repo="website-monitor-lambda"`

### **3. Deploy Pipeline**
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deploy the pipeline
cdk deploy
```

## 📋 Pipeline Features

### **Automated Testing**
- **Unit Tests**: PyTest framework
- **Integration Tests**: AWS service integration
- **Code Quality**: Linting and validation
- **Test Blockers**: Failed tests prevent deployment

### **Multi-Environment Deployment**
- **Beta**: For development and testing
- **Gamma**: For staging and pre-production validation
- **Production**: For live application

### **Security & Compliance**
- **IAM Roles**: Least privilege access
- **S3 Encryption**: Artifacts encrypted at rest
- **Parameter Store**: Secure token storage
- **CloudTrail**: Audit logging

## 🧪 Testing

### **Run Tests Locally**
```bash
# Install test dependencies
pip install pytest boto3 moto

# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_website_monitor.py::test_lambda_handler -v

# Run CRUD API tests
python -m pytest tests/test_crud_api.py -v
```

### **Test Coverage**
- **Unit Tests**: Lambda function unit tests
- **Functional Tests**: End-to-end workflow testing
- **Integration Tests**: AWS service integration
- **CRUD API Tests**: Create, Read, Update, Delete operations ✅
- **DynamoDB Performance Tests**: Read/write time validation ✅
- **Error Handling**: Edge cases and failure scenarios
- **CORS Testing**: Cross-origin resource sharing validation ✅

## 🌐 CRUD API Usage

### **API Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/websites` | List all target websites |
| GET | `/websites/{id}` | Get specific website |
| POST | `/websites` | Create new website |
| PUT | `/websites/{id}` | Update website |
| DELETE | `/websites/{id}` | Delete website |

### **Quick Start Examples**

```bash
# List all websites
curl -X GET https://your-api-gateway-url/websites

# Create a new website
curl -X POST https://your-api-gateway-url/websites \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "name": "Example Website",
    "description": "A sample website",
    "enabled": true
  }'

# Update a website
curl -X PUT https://your-api-gateway-url/websites/{id} \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# Delete a website
curl -X DELETE https://your-api-gateway-url/websites/{id}
```

### **API Documentation**
📖 [Complete API Documentation](API_DOCUMENTATION.md)

## 🎯 **Project Implementation Status**

### ✅ **Project 1: Website Monitoring System - COMPLETED**
- ✅ **Canary Lambda function** - Website crawler with availability/latency monitoring
- ✅ **Web crawler** - Crawls websites from DynamoDB target list
- ✅ **5-minute cadence** - EventBridge rule triggers every 5 minutes
- ✅ **CloudWatch metrics** - Availability, latency, response size metrics
- ✅ **CloudWatch Dashboard** - Real-time monitoring dashboard
- ✅ **CloudWatch Alarms** - Threshold-based alarms for availability/latency
- ✅ **SNS notifications** - Email alerts with proper tagging
- ✅ **DynamoDB logging** - Alarm history stored in DynamoDB
- ✅ **Multi-stage pipeline** - Alpha/Beta/Gamma/Prod with test blockers
- ✅ **Unit/Integration tests** - Comprehensive test coverage
- ✅ **Operational health monitoring** - Memory, duration, error metrics
- ✅ **Automated rollback** - Blue-green deployment with alarm-based rollback

### ✅ **Project 2: CRUD API Gateway - COMPLETED**
- ✅ **CRUD API Gateway** - RESTful endpoints for website management
- ✅ **CRUD Lambda function** - Handles Create/Read/Update/Delete operations
- ✅ **DynamoDB target list** - Separate table for website management
- ✅ **REST endpoints** - GET, POST, PUT, DELETE operations
- ✅ **API Gateway integration** - Full CDK implementation
- ✅ **CORS support** - Cross-origin resource sharing enabled
- ✅ **Real-time integration** - Web crawler reads from API-managed database
- ✅ **Performance testing** - DynamoDB read/write time validation
- ✅ **Error handling** - Comprehensive error responses and validation

## 📊 Monitoring & Observability

### **Pipeline Monitoring**
- **CodePipeline Console**: Visual pipeline status
- **CloudWatch Logs**: Build and deployment logs
- **SNS Notifications**: Pipeline status alerts
- **CloudTrail**: API call auditing

### **Application Monitoring**
- **CloudWatch Dashboard**: Real-time metrics
- **Alarms**: Automated alerting
- **DynamoDB**: Alarm history logging
- **SNS**: Email notifications

### **Week 11: Operational Health Monitoring & Blue-Green Deployment**

#### **Lambda Operational Metrics**
The system now monitors critical Lambda operational health metrics:

- **Invocations**: Tracks Lambda function calls (alerts if < 1 invocation)
- **Duration**: Monitors execution time (alerts if > 25 seconds)
- **Errors**: Detects function errors (alerts if > 0 errors)
- **Memory Utilization**: Tracks memory usage (alerts if > 80%)

#### **Blue-Green Deployment with Automated Rollback**
- **Lambda Alias**: Creates a "Prod" alias for seamless traffic shifting
- **CodeDeploy Integration**: Implements canary deployment strategy
- **Canary Configuration**: 10% traffic for 5 minutes before full deployment
- **Automated Rollback**: Automatically rolls back if operational alarms trigger
- **Deployment Group**: Links operational alarms to deployment decisions

#### **Operational Alarms Configuration**
```python
# Invocations Alarm
invocations_alarm = cloudwatch.Alarm(
    metric=wh_lambda.metric_invocations(),
    threshold=1,
    comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD
)

# Duration Alarm  
duration_alarm = cloudwatch.Alarm(
    metric=wh_lambda.metric_duration(),
    threshold=25000,  # 25 seconds
    comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
)

# Error Alarm
error_alarm = cloudwatch.Alarm(
    metric=wh_lambda.metric_errors(),
    threshold=0,
    comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
)

# Memory Alarm
memory_alarm = cloudwatch.Alarm(
    metric=wh_lambda.metric("MemoryUtilization"),
    threshold=80,  # 80% utilization
    comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
)
```

#### **Deployment Group Setup**
```python
deployment_group = codedeploy.LambdaDeploymentGroup(
    alias=alias,
    deployment_config=codedeploy.LambdaDeploymentConfig.CANARY_10_PERCENT_5_MINUTES,
    alarms=[invocations_alarm, duration_alarm, error_alarm, memory_alarm]
)
```

#### **Rollback Automation**
- **Automatic Detection**: CloudWatch alarms monitor key metrics during deployment
- **Immediate Response**: Alarms trigger within 1-2 evaluation periods
- **Traffic Shifting**: CodeDeploy automatically shifts traffic back to previous version
- **Notification**: SNS alerts notify team of rollback events
- **Audit Trail**: All rollback events logged in CloudWatch and CloudTrail

## 🔄 Pipeline Workflow

### **Automatic Trigger**
1. Developer pushes code to GitHub
2. Pipeline automatically starts
3. Code is built and tested
4. If tests pass, deploys to Beta
5. Manual approval for Gamma
6. Manual approval for Production

### **Manual Trigger**
```bash
# Start pipeline manually
aws codepipeline start-pipeline-execution \
  --name WebsiteMonitorPipeline
```

## 🛠️ Customization

### **Adding New Stages**
```python
# Add new stage to pipeline
new_stage = WebsiteMonitorStage(
    self, "NewStage",
    env=Environment(account=self.account, region=self.region)
)
```

### **Modifying Build Process**
Edit the `build_spec` in `pipeline_project_stack.py`:
```python
build_spec=codebuild.BuildSpec.from_object({
    "version": "0.2",
    "phases": {
        "install": {
            "commands": [
                "pip install your-additional-packages"
            ]
        },
        # ... other phases
    }
})
```

### **Environment-Specific Configuration**
```python
# Different configurations per stage
beta_config = {"environment": "beta", "debug": True}
gamma_config = {"environment": "gamma", "debug": False}
prod_config = {"environment": "prod", "debug": False}
```

## 📈 Best Practices

### **Code Quality**
- Write comprehensive unit tests
- Use type hints and documentation
- Follow PEP 8 style guidelines
- Implement proper error handling

### **Security**
- Use least privilege IAM roles
- Store secrets in Parameter Store
- Enable CloudTrail logging
- Regular security audits

### **Monitoring**
- Set up comprehensive alarms
- Monitor pipeline performance
- Track deployment metrics
- Implement rollback procedures

## 🚨 Troubleshooting

### **Common Issues**

#### **Pipeline Fails at Build Stage**
- Check CodeBuild logs in CloudWatch
- Verify all dependencies are installed
- Ensure tests are passing

#### **Deployment Fails**
- Check CloudFormation stack events
- Verify IAM permissions
- Check resource limits

#### **GitHub Integration Issues**
- Verify token is valid and has correct permissions
- Check repository name and branch
- Ensure webhook is configured correctly

### **Debug Commands**
```bash
# Check pipeline status
aws codepipeline get-pipeline-state --name WebsiteMonitorPipeline

# View build logs
aws logs describe-log-groups --log-group-name-prefix "/aws/codebuild/WebsiteMonitorBuild"

# Check CloudFormation stacks
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE
```

## 📚 Documentation

- **AWS CodePipeline**: https://docs.aws.amazon.com/codepipeline/
- **AWS CodeBuild**: https://docs.aws.amazon.com/codebuild/
- **AWS CDK**: https://docs.aws.amazon.com/cdk/
- **PyTest**: https://docs.pytest.org/

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Pipeline Status**: ✅ Active  
**Last Updated**: Week 11 - Operational Monitoring & Blue-Green Deployment  
**Version**: 1.1.0
