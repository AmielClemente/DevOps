# 🔧 Website Health Monitoring System - Operational Runbook

## 📋 Overview
This runbook provides operational procedures for the Website Health Monitoring System, including troubleshooting, maintenance, and emergency response procedures.

---

## 🚨 Emergency Response Procedures

### **Critical System Down**
**Symptoms**: All websites showing 0% availability
**Immediate Actions**:
1. Check CloudWatch Dashboard for system-wide issues
2. Verify Lambda function execution logs
3. Check AWS service status page
4. Review EventBridge rule status

**Escalation**:
- **Level 1**: Check Lambda logs in CloudWatch
- **Level 2**: Verify IAM permissions and service limits
- **Level 3**: Contact AWS support if service-wide issue

### **False Alarm Storm**
**Symptoms**: Multiple alarms triggering simultaneously
**Immediate Actions**:
1. Check if monitored websites are actually down
2. Verify alarm thresholds in constants.py
3. Review recent code changes
4. Check for network connectivity issues

---

## 🔍 Troubleshooting Guide

### **Lambda Function Issues**

#### **Website Crawler Lambda Not Executing**
```bash
# Check EventBridge rule
aws events list-rules --name-prefix "ScheduleRule"

# Check Lambda function status
aws lambda get-function --function-name "WebsiteCrawlerLambda"

# Review execution logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/WebsiteCrawlerLambda"
```

#### **Alarm Logger Lambda Not Writing to DynamoDB**
```bash
# Check DynamoDB table
aws dynamodb describe-table --table-name "WebsiteAlarmTable"

# Verify Lambda permissions
aws iam get-role-policy --role-name "AlarmLoggerLambda-role" --policy-name "DynamoDBWritePolicy"

# Check Lambda logs
aws logs filter-log-events --log-group-name "/aws/lambda/AlarmLoggerLambda"
```

### **CloudWatch Issues**

#### **Metrics Not Appearing**
1. Check Lambda execution logs for errors
2. Verify metric namespace: `amiel-week3`
3. Check IAM permissions for CloudWatch PutMetricData
4. Verify metric dimensions and names

#### **Alarms Not Triggering**
1. Check alarm configuration in CloudWatch console
2. Verify threshold values match constants.py
3. Check alarm state and evaluation periods
4. Review SNS topic subscriptions

### **SNS Notification Issues**

#### **No Email Notifications**
1. Check SNS topic subscriptions
2. Verify email address configuration
3. Check spam/junk folders
4. Verify SNS topic permissions

---

## 📊 Monitoring & Maintenance

### **Daily Health Checks**
1. **Dashboard Review**: Check CloudWatch dashboard for any anomalies
2. **Alarm Status**: Verify all alarms are in OK state
3. **Lambda Logs**: Review recent execution logs for errors
4. **DynamoDB Items**: Check for unusual alarm patterns

### **Weekly Maintenance**
1. **Threshold Review**: Analyze alarm frequency and adjust if needed
2. **Log Cleanup**: Review and archive old CloudWatch logs
3. **Performance Analysis**: Review Lambda execution times and errors
4. **Documentation Update**: Update any operational procedures

### **Monthly Tasks**
1. **Cost Review**: Analyze AWS costs and optimize if needed
2. **Security Review**: Check IAM permissions and access patterns
3. **Capacity Planning**: Review DynamoDB usage and scaling needs
4. **Disaster Recovery**: Test backup and recovery procedures

---

## 🔧 Configuration Management

### **Adding New URLs**
1. Edit `website_monitor_cdk/constants.py`
2. Add URL to the `URLS` list
3. Deploy changes: `cdk deploy`
4. Verify new alarms are created
5. Test monitoring for new URL

### **Modifying Alarm Thresholds**
1. Update values in `website_monitor_cdk/constants.py`:
   ```python
   AVAIL_THRESHOLD = 0.99  # 99% availability
   LATENCY_THRESHOLD_MS = 500  # 500ms latency
   RESPONSE_SIZE_MIN_BYTES = 1  # 1 byte minimum
   ```
2. Deploy changes: `cdk deploy`
3. Verify alarm configurations updated
4. Test threshold changes

### **Changing Alert Email**
1. Update `ALERT_EMAIL` in `website_monitor_cdk/constants.py`
2. Deploy changes: `cdk deploy`
3. Verify SNS subscription updated
4. Test email notifications

---

## 📈 Performance Monitoring

### **Key Metrics to Track**
- **Lambda Execution Duration**: Should be < 30 seconds
- **Lambda Error Rate**: Should be < 1%
- **Alarm Response Time**: Should be < 1 minute
- **DynamoDB Write Capacity**: Monitor for throttling
- **CloudWatch API Calls**: Monitor for rate limiting

### **Performance Optimization**
1. **Lambda Optimization**:
   - Use connection pooling for HTTP requests
   - Implement proper error handling
   - Optimize memory allocation

2. **DynamoDB Optimization**:
   - Monitor read/write capacity
   - Implement proper indexing
   - Use batch operations where possible

3. **CloudWatch Optimization**:
   - Batch metric data where possible
   - Use appropriate metric periods
   - Implement proper dimension usage

---

## 🛡️ Security Procedures

### **Access Management**
1. **IAM Roles**: Regularly review Lambda execution roles
2. **Permissions**: Follow principle of least privilege
3. **Secrets**: Use AWS Secrets Manager for sensitive data
4. **Audit**: Regular access log reviews

### **Data Protection**
1. **DynamoDB Encryption**: Ensure encryption at rest is enabled
2. **Log Encryption**: Verify CloudWatch logs are encrypted
3. **Network Security**: Use VPC endpoints where appropriate
4. **Data Retention**: Implement proper data retention policies

---

## 🔄 Backup & Recovery

### **Backup Procedures**
1. **Code Backup**: All code is version controlled in GitHub
2. **Configuration Backup**: CDK stack configuration is in code
3. **Data Backup**: DynamoDB point-in-time recovery enabled
4. **Documentation Backup**: All documentation in repository

### **Recovery Procedures**
1. **Infrastructure Recovery**: Use CDK to redeploy entire stack
2. **Data Recovery**: Use DynamoDB point-in-time recovery
3. **Configuration Recovery**: Restore from version control
4. **Documentation Recovery**: Clone from GitHub repository

---

## 📞 Support Contacts

### **Internal Support**
- **Primary Developer**: Amiel Clemente
- **Email**: 22070210@student.westernsydney.edu.au
- **Response Time**: 24 hours for non-critical issues

### **AWS Support**
- **Support Level**: Basic (free tier)
- **Escalation**: For service-wide issues
- **Documentation**: AWS Support Center

### **Emergency Contacts**
- **Critical Issues**: Immediate response required
- **Service Outages**: Escalate to AWS support
- **Security Issues**: Follow incident response procedures

---

## 📋 Operational Checklists

### **Pre-Deployment Checklist**
- [ ] Code reviewed and tested
- [ ] Documentation updated
- [ ] Backup procedures verified
- [ ] Rollback plan prepared
- [ ] Stakeholders notified

### **Post-Deployment Checklist**
- [ ] All services running normally
- [ ] Alarms in OK state
- [ ] Dashboard showing correct data
- [ ] Notifications working
- [ ] Logs clean and error-free

### **Monthly Health Check**
- [ ] Review all alarm configurations
- [ ] Analyze performance metrics
- [ ] Check security configurations
- [ ] Update documentation
- [ ] Review costs and optimization opportunities

---

## 🎯 Success Metrics

### **Operational KPIs**
- **Uptime**: 99.9% system availability
- **Response Time**: < 1 minute alarm response
- **Error Rate**: < 1% Lambda execution errors
- **Coverage**: 100% of configured URLs monitored

### **Business KPIs**
- **Alert Accuracy**: < 5% false positive rate
- **Mean Time to Detection**: < 5 minutes
- **Mean Time to Resolution**: < 30 minutes
- **Customer Satisfaction**: High confidence in monitoring

---

*Last Updated: [Current Date]*  
*Version: 1.0*  
*Next Review: Monthly*

