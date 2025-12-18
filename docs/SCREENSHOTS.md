# Project Screenshots Guide

## 📸 Screenshots to Capture

### 1. AWS CloudFormation Console
- **URL**: https://us-east-1.console.aws.amazon.com/cloudformation/
- **What to show**: All 4 stacks with CREATE_COMPLETE status
- **Filename**: `cloudformation-stacks.png`

### 2. Lambda Functions
- **URL**: https://us-east-1.console.aws.amazon.com/lambda/
- **What to show**: devops-multiregion-api-handler function
- **Filename**: `lambda-functions.png`

### 3. DynamoDB Table
- **URL**: https://us-east-1.console.aws.amazon.com/dynamodbv2/
- **What to show**: DevOpsMetrics table
- **Filename**: `dynamodb-table.png`

### 4. CodePipeline
- **URL**: https://us-east-1.console.aws.amazon.com/codesuite/codepipeline/
- **What to show**: devops-multiregion-pipeline execution
- **Filename**: `codepipeline-dashboard.png`

### 5. API Gateway
- **URL**: https://us-east-1.console.aws.amazon.com/apigateway/
- **What to show**: HTTP API with routes
- **Filename**: `api-gateway.png`

### 6. CloudWatch Dashboard
- **URL**: https://us-east-1.console.aws.amazon.com/cloudwatch/
- **What to show**: Metrics and logs
- **Filename**: `cloudwatch-monitoring.png`

## 🔄 How to Update README

After taking screenshots:

1. Save images in `docs/images/` folder
2. Update README.md image URLs:
   ```markdown
   ![CloudFormation Stacks](./docs/images/cloudformation-stacks.png)
   ```
3. Commit and push changes

## 📱 Screenshot Tips

- Use full browser window
- Ensure all important information is visible
- Use high resolution (at least 1200px wide)
- Crop unnecessary browser chrome
- Show successful/completed states