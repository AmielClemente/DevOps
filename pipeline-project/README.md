# 🚀 Website Monitoring CI/CD Pipeline

A comprehensive CI/CD pipeline built with AWS CodePipeline and CDK that automatically builds, tests, and deploys the Website Monitoring Application across multiple environments.

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
- **Beta**: Development/testing environment
- **Gamma**: Staging environment (pre-production)
- **Production**: Live environment

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
pip install pytest boto3

# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_website_monitor.py::test_lambda_handler -v
```

### **Test Coverage**
- Lambda function unit tests
- CDK stack creation tests
- Integration tests with AWS services
- Error handling and edge cases

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
**Last Updated**: [Current Date]  
**Version**: 1.0.0