# Complete Setup Guide

## Prerequisites Checklist
- [ ] AWS Account (Free Tier activated)
- [ ] AWS CLI installed
- [ ] Git installed
- [ ] Python 3.9+ installed
- [ ] Text editor (VS Code recommended)

## Step-by-Step Setup

### 1. AWS CLI Configuration
```bash
# Install AWS CLI (if not installed)
# Windows: Download from https://aws.amazon.com/cli/

# Configure AWS CLI
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1
# Default output format: json
```

### 2. Verify AWS Configuration
```bash
# Test AWS connection
aws sts get-caller-identity

# Should return your account details
```

### 3. Initialize Git Repository
```bash
cd C:\Users\TANISHA\desktop\devops-aws-multiregion-pipeline

git init
git add .
git commit -m "Initial commit: DevOps Multi-Region Pipeline"
```

### 4. Deploy Infrastructure

#### Option A: Manual Deployment (Recommended for learning)

**Step 1: Deploy Pipeline**
```bash
aws cloudformation create-stack ^
  --stack-name devops-pipeline ^
  --template-body file://infrastructure/cloudformation/01-pipeline.yaml ^
  --capabilities CAPABILITY_IAM ^
  --region us-east-1
```

Wait 2-3 minutes, then check status:
```bash
aws cloudformation describe-stacks --stack-name devops-pipeline --region us-east-1
```

**Step 2: Deploy Database**
```bash
aws cloudformation create-stack ^
  --stack-name devops-database ^
  --template-body file://infrastructure/cloudformation/03-database.yaml ^
  --region us-east-1
```

**Step 3: Deploy Lambda & API**
```bash
aws cloudformation create-stack ^
  --stack-name devops-app ^
  --template-body file://infrastructure/cloudformation/02-lambda-api.yaml ^
  --capabilities CAPABILITY_IAM ^
  --region us-east-1
```

**Step 4: Deploy Monitoring**
```bash
aws cloudformation create-stack ^
  --stack-name devops-monitoring ^
  --template-body file://infrastructure/cloudformation/04-monitoring.yaml ^
  --parameters ParameterKey=AlertEmail,ParameterValue=your-email@example.com ^
  --region us-east-1
```

### 5. Get Repository URL
```bash
aws cloudformation describe-stacks ^
  --stack-name devops-pipeline ^
  --query "Stacks[0].Outputs[?OutputKey=='RepositoryCloneUrlHttp'].OutputValue" ^
  --output text ^
  --region us-east-1
```

### 6. Configure Git Credentials for CodeCommit

**Option 1: HTTPS Git Credentials (Easiest)**
1. Go to AWS Console → IAM → Users → Your User
2. Security Credentials tab
3. Scroll to "HTTPS Git credentials for AWS CodeCommit"
4. Click "Generate credentials"
5. Save username and password

**Option 2: Git Credential Helper**
```bash
git config --global credential.helper "!aws codecommit credential-helper $@"
git config --global credential.UseHttpPath true
```

### 7. Push Code to CodeCommit
```bash
# Add CodeCommit as remote (use URL from step 5)
git remote add origin <YOUR_CODECOMMIT_URL>

# Push code
git push origin main
```

### 8. Monitor Pipeline
```bash
# Check pipeline status
aws codepipeline get-pipeline-state --name devops-multiregion-pipeline --region us-east-1
```

Or visit AWS Console → CodePipeline

### 9. Test API
```bash
# Get API endpoint
aws cloudformation describe-stacks ^
  --stack-name devops-app ^
  --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" ^
  --output text ^
  --region us-east-1

# Test health endpoint
curl <API_ENDPOINT>/health
```

## Troubleshooting

### Issue: Stack creation failed
```bash
# Check stack events
aws cloudformation describe-stack-events --stack-name <STACK_NAME> --region us-east-1
```

### Issue: Git push authentication failed
- Verify Git credentials are correct
- Try credential helper method
- Check IAM user has CodeCommit permissions

### Issue: Lambda function not updating
- Check CodeBuild logs in AWS Console
- Verify S3 bucket permissions
- Check buildspec.yml syntax

## Verification Checklist
- [ ] All CloudFormation stacks show CREATE_COMPLETE
- [ ] CodePipeline shows successful execution
- [ ] API health endpoint returns 200 OK
- [ ] CloudWatch dashboard shows metrics
- [ ] SNS email subscription confirmed

## Next Steps
1. Add more Lambda functions
2. Implement automated tests
3. Set up DR region deployment
4. Create custom CloudWatch metrics
5. Add API authentication

## Cleanup (When Done)
```bash
# Delete stacks in reverse order
aws cloudformation delete-stack --stack-name devops-monitoring --region us-east-1
aws cloudformation delete-stack --stack-name devops-app --region us-east-1
aws cloudformation delete-stack --stack-name devops-database --region us-east-1
aws cloudformation delete-stack --stack-name devops-pipeline --region us-east-1

# Empty and delete S3 bucket manually from console
```

## Cost Monitoring
All services used are within AWS Free Tier:
- CodeCommit: 5 users, 50GB storage
- CodeBuild: 100 build minutes/month
- CodePipeline: 1 pipeline/month
- Lambda: 1M requests/month
- API Gateway: 1M requests/month
- DynamoDB: 25GB storage
- CloudWatch: 10 metrics, 5GB logs

**Estimated Cost: $0/month** (within free tier limits)
