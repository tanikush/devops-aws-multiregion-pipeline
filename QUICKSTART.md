# Quick Start Guide (Hindi + English)

## 🚀 Abhi Shuru Karo / Start Now

### Step 1: AWS Account Setup
1. AWS account banao (agar nahi hai): https://aws.amazon.com/free
2. Free Tier activate karo
3. IAM user banao with Administrator access
4. Access Key download karo

### Step 2: AWS CLI Install & Configure
```bash
# AWS CLI install karo
# Download from: https://aws.amazon.com/cli/

# Configure karo
aws configure
# Access Key ID: <your-key>
# Secret Access Key: <your-secret>
# Region: us-east-1
# Output: json
```

### Step 3: Test AWS Connection
```bash
aws sts get-caller-identity
```
Agar account details dikhe, to sab theek hai! ✓

### Step 4: Git Initialize
```bash
cd C:\Users\TANISHA\desktop\devops-aws-multiregion-pipeline
git init
git add .
git commit -m "Initial commit"
```

### Step 5: Deploy Pipeline (Sabse Pehle)
```bash
aws cloudformation create-stack --stack-name devops-pipeline --template-body file://infrastructure/cloudformation/01-pipeline.yaml --capabilities CAPABILITY_IAM --region us-east-1
```

**Wait 2-3 minutes**, phir check karo:
```bash
aws cloudformation describe-stacks --stack-name devops-pipeline --region us-east-1
```

Status "CREATE_COMPLETE" hona chahiye!

### Step 6: Deploy Database
```bash
aws cloudformation create-stack --stack-name devops-database --template-body file://infrastructure/cloudformation/03-database.yaml --region us-east-1
```

### Step 7: Deploy Application
```bash
aws cloudformation create-stack --stack-name devops-app --template-body file://infrastructure/cloudformation/02-lambda-api.yaml --capabilities CAPABILITY_IAM --region us-east-1
```

### Step 8: Deploy Monitoring
```bash
aws cloudformation create-stack --stack-name devops-monitoring --template-body file://infrastructure/cloudformation/04-monitoring.yaml --parameters ParameterKey=AlertEmail,ParameterValue=your-email@example.com --region us-east-1
```

### Step 9: Get CodeCommit URL
```bash
aws cloudformation describe-stacks --stack-name devops-pipeline --query "Stacks[0].Outputs[?OutputKey=='RepositoryCloneUrlHttp'].OutputValue" --output text --region us-east-1
```

### Step 10: Setup Git Credentials
**AWS Console mein jao:**
1. IAM → Users → Your User
2. Security Credentials tab
3. "HTTPS Git credentials for AWS CodeCommit"
4. Generate credentials
5. Username aur password save karo

### Step 11: Push Code
```bash
git remote add origin <YOUR_CODECOMMIT_URL>
git push origin main
```
Username aur password enter karo (step 10 se)

### Step 12: Check Pipeline
AWS Console → CodePipeline → devops-multiregion-pipeline

Pipeline automatically run hoga! 🎉

### Step 13: Test API
```bash
# API endpoint nikalo
aws cloudformation describe-stacks --stack-name devops-app --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" --output text --region us-east-1

# Test karo (browser mein ya curl se)
curl <API_ENDPOINT>/health
```

Response aana chahiye:
```json
{
  "status": "healthy",
  "region": "us-east-1",
  "timestamp": "2025-12-18T...",
  "service": "DevOps Monitor API"
}
```

## ✅ Success! Tumhara Project Live Hai!

## 📊 Ab Kya Dekho?

1. **AWS Console → CodePipeline**: Pipeline status
2. **AWS Console → Lambda**: Functions
3. **AWS Console → API Gateway**: API endpoints
4. **AWS Console → CloudWatch**: Dashboards & Logs
5. **AWS Console → DynamoDB**: Tables

## 🎯 Resume Mein Kya Likho?

Dekho: `docs/RESUME_POINTS.md`

## 🐛 Problem Ho To?

### Error: Stack already exists
```bash
# Delete karo aur phir se try karo
aws cloudformation delete-stack --stack-name <STACK_NAME> --region us-east-1
```

### Error: Git push failed
- Git credentials check karo
- IAM user ko CodeCommit permission hai?

### Error: Lambda not updating
- CodeBuild logs dekho AWS Console mein
- buildspec.yml syntax check karo

## 📚 Complete Documentation

- **Setup Guide**: `docs/SETUP_GUIDE.md`
- **Resume Points**: `docs/RESUME_POINTS.md`
- **Main README**: `README.md`

## 💡 Pro Tips

1. **CloudWatch Logs**: Har Lambda function ke logs CloudWatch mein milenge
2. **Cost Monitoring**: AWS Console → Billing → Free Tier usage check karo
3. **Email Alerts**: SNS subscription confirm karo email se
4. **Testing**: `src/tests/test_api.py` run karo locally

## 🎓 Learning Path

1. ✅ Basic setup (ye guide)
2. 📖 Understand CloudFormation templates
3. 🔧 Modify Lambda functions
4. 🧪 Add more tests
5. 🌍 Deploy to DR region (us-west-2)
6. 📊 Custom CloudWatch metrics
7. 🔐 Add API authentication

## 🤝 Help Chahiye?

1. AWS Documentation: https://docs.aws.amazon.com
2. CloudFormation Docs: https://docs.aws.amazon.com/cloudformation
3. Lambda Docs: https://docs.aws.amazon.com/lambda

---

**Good Luck! 🚀 Tumhara DevOps journey shuru ho gaya hai!**
