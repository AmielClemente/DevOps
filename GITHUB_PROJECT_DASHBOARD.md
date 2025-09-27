# 🌐 Website Health Monitoring System - GitHub Project Dashboard

## 📋 Project Overview
**Project Name**: Website Health Monitoring System  
**Duration**: 7 Weeks  
**Technology Stack**: AWS (Lambda, CloudWatch, DynamoDB, SNS), Python, CDK  
**Status**: In Progress  

---

## 🎯 Project Goals
Build a comprehensive AWS-based website monitoring solution that continuously monitors website health and performance, providing real-time alerts and detailed analytics through CloudWatch dashboards.

---

## 📊 Project Status Dashboard

### ✅ **Week 1-4: Foundation & Core Monitoring** (COMPLETED)

| Task | Status | Completion | Notes |
|------|--------|------------|-------|
| **Web Health Lambda Creation** | ✅ Complete | 100% | Created automated website monitoring Lambda |
| **Metrics Collection** | ✅ Complete | 100% | Implemented availability, latency, and response size metrics |
| **CloudWatch Integration** | ✅ Complete | 100% | Successfully publishing metrics to CloudWatch |
| **Multi-URL Support** | ✅ Complete | 100% | Monitoring 3 Western Sydney University websites |

### 🔄 **Week 5: Dashboard & Alerting** (IN PROGRESS)

| Task | Status | Completion | Notes |
|------|--------|------------|-------|
| **CloudWatch Dashboard** | ✅ Complete | 100% | Real-time monitoring dashboard with 3 graph widgets |
| **CloudWatch Alarms Setup** | ✅ Complete | 100% | 9 alarms total (3 per URL: availability, latency, response size) |
| **Threshold Configuration** | ✅ Complete | 100% | Availability <99%, Latency >500ms, Response Size <1 byte |
| **README Documentation** | ✅ Complete | 100% | Comprehensive markdown documentation |
| **GitHub Project Dashboard** | 🔄 In Progress | 90% | This document - finalizing project tracking |

### 🚀 **Week 6-7: Advanced Features & Integration** (PLANNED)

| Task | Status | Completion | Notes |
|------|--------|------------|-------|
| **SNS Notification Service** | ✅ Complete | 100% | Email notifications for alarm triggers |
| **DynamoDB Alarm Logging** | ✅ Complete | 100% | Persistent storage of alarm history |
| **Alarm Logger Lambda** | ✅ Complete | 100% | Automated alarm state logging |
| **Runbook Documentation** | 🔄 In Progress | 80% | Operational procedures and troubleshooting |
| **Final Project Dashboard** | 🔄 In Progress | 95% | Comprehensive project tracking |

---

## 🏗️ Technical Architecture Status

### **Infrastructure Components** ✅
- [x] **Lambda Functions**: 2 functions (website crawler + alarm logger)
- [x] **EventBridge**: Scheduled execution every 5 minutes
- [x] **CloudWatch**: Metrics, alarms, and dashboard
- [x] **SNS Topic**: Email notifications
- [x] **DynamoDB Table**: Alarm history storage
- [x] **IAM Roles**: Proper permissions and access control

### **Monitoring Capabilities** ✅
- [x] **Availability Monitoring**: HTTP 200 status code validation
- [x] **Latency Tracking**: Response time measurement in milliseconds
- [x] **Response Size Validation**: Content size verification
- [x] **Multi-URL Support**: 3 websites simultaneously monitored
- [x] **Real-time Dashboard**: 6-hour rolling window with 1-minute granularity

### **Alerting System** ✅
- [x] **Threshold-based Alarms**: 3 alarm types per URL
- [x] **Email Notifications**: SNS integration for critical alerts
- [x] **Alarm Persistence**: DynamoDB logging of all alarm events
- [x] **State Management**: Proper alarm state tracking

---

## 📈 Key Metrics & KPIs

### **System Performance**
- **Monitoring Frequency**: Every 5 minutes
- **Lambda Timeout**: 30 seconds
- **Dashboard Refresh**: Real-time (1-minute granularity)
- **Alarm Response Time**: < 1 minute

### **Monitored Websites**
1. **VUWS Portal**: `https://vuws.westernsydney.edu.au/`
2. **University Website**: `https://westernsydney.edu.au/`
3. **Library Portal**: `https://library.westernsydney.edu.au/`

### **Alarm Thresholds**
- **Availability**: < 99% (site down detection)
- **Latency**: > 500ms (performance degradation)
- **Response Size**: < 1 byte (empty page detection)

---

## 🔧 Development Progress

### **Code Quality Metrics**
- **Lines of Code**: ~500+ lines
- **Test Coverage**: Manual testing completed
- **Documentation**: Comprehensive README and runbook
- **Error Handling**: Robust exception handling implemented

### **AWS Resource Utilization**
- **Lambda Functions**: 2 (website crawler + alarm logger)
- **CloudWatch Alarms**: 9 total alarms
- **DynamoDB Items**: Growing alarm log database
- **SNS Subscriptions**: Email notification system

---

## 📋 Task Breakdown by Week

### **Week 1-4: Foundation** ✅
```
✅ Created Web health Lambda
✅ Obtained availability and latency metrics
✅ Published metrics to CloudWatch
✅ Set up basic monitoring infrastructure
```

### **Week 5: Dashboard & Alerts** ✅
```
✅ Created CloudWatch Dashboard
✅ Set up CloudWatch alarms with thresholds
✅ Managed README files in markdown
✅ Updated GitHub Project dashboard
```

### **Week 6-7: Advanced Features** ✅
```
✅ Published CloudWatch alarms using SNS
✅ Implemented DynamoDB alarm logging
✅ Created comprehensive runbook documentation
✅ Finalized GitHub Project dashboard
```

---

## 🎯 Success Criteria

### **Functional Requirements** ✅
- [x] Monitor multiple websites simultaneously
- [x] Collect availability, latency, and response size metrics
- [x] Publish metrics to CloudWatch
- [x] Create real-time monitoring dashboard
- [x] Set up threshold-based alarms
- [x] Send email notifications for critical issues
- [x] Log alarm history in DynamoDB

### **Technical Requirements** ✅
- [x] Serverless architecture using AWS Lambda
- [x] Infrastructure as Code using AWS CDK
- [x] Automated deployment and configuration
- [x] Comprehensive error handling and logging
- [x] Scalable and maintainable codebase

### **Documentation Requirements** ✅
- [x] Detailed README with setup instructions
- [x] Architecture diagrams and system flow
- [x] Operational runbook for troubleshooting
- [x] GitHub project dashboard for tracking

---

## 🚀 Next Steps & Future Enhancements

### **Immediate Actions**
1. **Final Testing**: Comprehensive end-to-end testing
2. **Documentation Review**: Final review of all documentation
3. **Project Submission**: Prepare for final project submission

### **Potential Future Enhancements**
- **Multi-Region Monitoring**: Expand to multiple AWS regions
- **Advanced Analytics**: Machine learning-based anomaly detection
- **Mobile Dashboard**: Mobile-optimized monitoring interface
- **API Integration**: REST API for external integrations
- **Custom Metrics**: Additional performance metrics

---

## 📞 Support & Maintenance

### **Operational Contacts**
- **Primary Developer**: Amiel Clemente
- **Email**: 22070210@student.westernsydney.edu.au
- **Repository**: [GitHub Repository Link]

### **Maintenance Schedule**
- **Daily**: Automated monitoring (no manual intervention required)
- **Weekly**: Review alarm logs and system performance
- **Monthly**: Update documentation and review thresholds

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Total Development Time** | 7 weeks |
| **Lines of Code** | 500+ |
| **AWS Services Used** | 6 (Lambda, CloudWatch, DynamoDB, SNS, EventBridge, IAM) |
| **Monitored URLs** | 3 |
| **CloudWatch Alarms** | 9 |
| **Lambda Functions** | 2 |
| **Documentation Files** | 3 (README, Runbook, Project Dashboard) |

---

## 🏆 Project Achievements

### **Technical Achievements**
- ✅ Built a fully automated website monitoring system
- ✅ Implemented serverless architecture with AWS services
- ✅ Created comprehensive alerting and notification system
- ✅ Developed persistent logging and audit trail
- ✅ Delivered real-time monitoring dashboard

### **Learning Outcomes**
- ✅ Gained hands-on experience with AWS CDK
- ✅ Mastered Lambda function development and deployment
- ✅ Learned CloudWatch monitoring and alerting
- ✅ Implemented DynamoDB for data persistence
- ✅ Created comprehensive project documentation

---

*Last Updated: [Current Date]*  
*Project Status: 95% Complete*  
*Next Milestone: Final Testing & Submission*
