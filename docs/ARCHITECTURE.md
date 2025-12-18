# Architecture Documentation

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DEVELOPER WORKFLOW                           │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ git push
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AWS CodeCommit (Git Repository)                   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Trigger
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         AWS CodePipeline                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│  │  Source  │───▶│  Build   │───▶│   Test   │───▶│  Deploy  │     │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Build
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          AWS CodeBuild                               │
│  • Run Tests                                                         │
│  • Package Lambda Functions                                         │
│  • Upload to S3                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Deploy
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PRIMARY REGION (us-east-1)                      │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    API Gateway (REST API)                   │    │
│  │                  https://api.example.com                    │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                  │                                   │
│                                  │ Invoke                            │
│                                  ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    AWS Lambda Functions                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │    │
│  │  │ API Handler  │  │ Health Check │  │ DR Replication│    │    │
│  │  │   (Python)   │  │   (Python)   │  │   (Python)   │    │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                  │                                   │
│                                  │ Read/Write                        │
│                                  ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              DynamoDB (DevOpsMetrics Table)                 │    │
│  │              • Deployment metrics                           │    │
│  │              • Health check data                            │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                  │                                   │
└──────────────────────────────────┼───────────────────────────────────┘
                                   │
                                   │ Replicate
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       DR REGION (us-west-2)                          │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              DynamoDB (DevOpsMetrics Table)                 │    │
│  │              • Replicated data                              │    │
│  │              • Standby for failover                         │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    MONITORING & ALERTING                             │
│                                                                       │
│  ┌──────────────────┐         ┌──────────────────┐                 │
│  │   CloudWatch     │         │   SNS Topics     │                 │
│  │   • Dashboards   │────────▶│   • Email Alerts │                 │
│  │   • Metrics      │         │   • Notifications│                 │
│  │   • Logs         │         └──────────────────┘                 │
│  │   • Alarms       │                                               │
│  └──────────────────┘                                               │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. CI/CD Pipeline
- **CodeCommit**: Git repository for source code
- **CodePipeline**: Orchestrates the entire deployment process
- **CodeBuild**: Builds and tests the application
- **S3**: Stores build artifacts

### 2. Application Layer
- **API Gateway**: REST API endpoint for external access
- **Lambda Functions**:
  - `api-handler`: Main API logic (GET/POST /metrics, GET /health)
  - `health-check`: Automated health monitoring
  - `dr-replication`: Cross-region data replication

### 3. Data Layer
- **DynamoDB (Primary)**: Main database in us-east-1
- **DynamoDB (DR)**: Replica database in us-west-2
- **Replication**: Automated via Lambda function

### 4. Monitoring
- **CloudWatch**: Metrics, logs, dashboards, alarms
- **SNS**: Email notifications for alerts
- **EventBridge**: Event-driven automation

## Data Flow

### Normal Operation Flow
1. User makes API request → API Gateway
2. API Gateway invokes Lambda function
3. Lambda reads/writes to DynamoDB
4. Response returned to user
5. Metrics logged to CloudWatch

### CI/CD Flow
1. Developer pushes code to CodeCommit
2. CodePipeline triggered automatically
3. CodeBuild runs tests and packages code
4. Artifacts uploaded to S3
5. Lambda functions updated automatically
6. Notification sent via SNS

### Disaster Recovery Flow
1. DR Lambda runs every 5 minutes (EventBridge)
2. Reads data from primary DynamoDB
3. Replicates to DR region DynamoDB
4. Logs replication status to CloudWatch
5. Alerts on failure via SNS

### Health Check Flow
1. EventBridge triggers health-check Lambda every 5 minutes
2. Lambda checks:
   - API Gateway availability
   - DynamoDB table status
   - Lambda function health
3. Sends metrics to CloudWatch
4. Triggers SNS alert if unhealthy

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      IAM Roles & Policies                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Lambda Execution Role                                       │
│  • CloudWatch Logs (write)                                   │
│  • DynamoDB (read/write)                                     │
│  • SNS (publish)                                             │
│                                                               │
│  CodeBuild Role                                              │
│  • S3 (read/write artifacts)                                 │
│  • CloudWatch Logs (write)                                   │
│  • CodeCommit (read)                                         │
│                                                               │
│  CodePipeline Role                                           │
│  • CodeCommit (read)                                         │
│  • CodeBuild (start/stop)                                    │
│  • S3 (read/write)                                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Security Best Practices Implemented
1. **Least Privilege**: Each role has minimum required permissions
2. **Encryption**: Data encrypted at rest (DynamoDB, S3)
3. **Private Resources**: S3 buckets block public access
4. **API Security**: API Gateway with throttling
5. **Secrets Management**: Environment variables for sensitive data

## Scalability

### Current Capacity (Free Tier)
- **API Gateway**: 1M requests/month
- **Lambda**: 1M invocations/month
- **DynamoDB**: 25GB storage, unlimited requests (on-demand)
- **CodeBuild**: 100 build minutes/month

### Scaling Strategy
1. **Horizontal Scaling**: Lambda auto-scales with requests
2. **Database Scaling**: DynamoDB on-demand pricing scales automatically
3. **Multi-Region**: DR region ready for failover
4. **Caching**: Can add CloudFront for API caching

## High Availability

### Availability Zones
- Lambda: Runs across multiple AZs automatically
- DynamoDB: Multi-AZ by default
- API Gateway: Multi-AZ by default

### Disaster Recovery
- **RTO (Recovery Time Objective)**: <5 minutes
- **RPO (Recovery Point Objective)**: <1 minute
- **Strategy**: Active-Passive (Primary in us-east-1, DR in us-west-2)

### Failover Process
1. Detect primary region failure (health check)
2. Update DNS/Route53 to point to DR region
3. DR region serves traffic
4. Data already replicated, minimal data loss

## Monitoring Strategy

### Metrics Tracked
1. **API Metrics**:
   - Request count
   - Error rate (4XX, 5XX)
   - Latency (p50, p99)

2. **Lambda Metrics**:
   - Invocation count
   - Error count
   - Duration
   - Concurrent executions

3. **Database Metrics**:
   - Read/Write capacity
   - Throttled requests
   - Item count

4. **Pipeline Metrics**:
   - Build success rate
   - Build duration
   - Deployment frequency

### Alerting Thresholds
- Lambda errors > 5 in 5 minutes → Alert
- API 5XX errors > 10 in 5 minutes → Alert
- Health check failure → Immediate alert
- Build failure → Immediate alert

## Cost Optimization

### Free Tier Usage
- All services within free tier limits
- Estimated monthly cost: $0

### Cost Monitoring
- CloudWatch billing alarms
- Monthly usage reports
- Free tier usage tracking

## Future Enhancements

1. **Blue-Green Deployment**: Zero-downtime deployments
2. **Canary Releases**: Gradual traffic shifting
3. **API Authentication**: Cognito or API keys
4. **Custom Domain**: Route53 + ACM certificate
5. **WAF**: Web Application Firewall for API
6. **X-Ray**: Distributed tracing
7. **Secrets Manager**: Centralized secrets management
8. **Multi-Region Active-Active**: Both regions serving traffic
