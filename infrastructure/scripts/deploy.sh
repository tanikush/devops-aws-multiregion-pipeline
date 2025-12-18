#!/bin/bash

# DevOps Multi-Region Pipeline Deployment Script
# This script deploys all CloudFormation stacks in the correct order

set -e

PROJECT_NAME="devops-multiregion"
PRIMARY_REGION="us-east-1"
DR_REGION="us-west-2"
ALERT_EMAIL="your-email@example.com"

echo "=========================================="
echo "DevOps Multi-Region Pipeline Deployment"
echo "=========================================="
echo ""

# Function to wait for stack creation
wait_for_stack() {
    local stack_name=$1
    local region=$2
    echo "Waiting for stack $stack_name to complete..."
    aws cloudformation wait stack-create-complete \
        --stack-name $stack_name \
        --region $region
    echo "✓ Stack $stack_name created successfully"
}

# Step 1: Deploy Pipeline (Primary Region)
echo "Step 1: Deploying CI/CD Pipeline..."
aws cloudformation create-stack \
    --stack-name ${PROJECT_NAME}-pipeline \
    --template-body file://infrastructure/cloudformation/01-pipeline.yaml \
    --parameters ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
    --capabilities CAPABILITY_IAM \
    --region $PRIMARY_REGION

wait_for_stack "${PROJECT_NAME}-pipeline" $PRIMARY_REGION

# Step 2: Deploy Database (Primary Region)
echo ""
echo "Step 2: Deploying DynamoDB Table (Primary Region)..."
aws cloudformation create-stack \
    --stack-name ${PROJECT_NAME}-database \
    --template-body file://infrastructure/cloudformation/03-database.yaml \
    --parameters ParameterKey=TableName,ParameterValue=DevOpsMetrics \
    --region $PRIMARY_REGION

wait_for_stack "${PROJECT_NAME}-database" $PRIMARY_REGION

# Step 3: Deploy Database (DR Region)
echo ""
echo "Step 3: Deploying DynamoDB Table (DR Region)..."
aws cloudformation create-stack \
    --stack-name ${PROJECT_NAME}-database-dr \
    --template-body file://infrastructure/cloudformation/03-database.yaml \
    --parameters ParameterKey=TableName,ParameterValue=DevOpsMetrics \
    --region $DR_REGION

wait_for_stack "${PROJECT_NAME}-database-dr" $DR_REGION

# Step 4: Deploy Lambda and API Gateway (Primary Region)
echo ""
echo "Step 4: Deploying Lambda Functions and API Gateway..."
aws cloudformation create-stack \
    --stack-name ${PROJECT_NAME}-app \
    --template-body file://infrastructure/cloudformation/02-lambda-api.yaml \
    --parameters \
        ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
        ParameterKey=TableName,ParameterValue=DevOpsMetrics \
    --capabilities CAPABILITY_IAM \
    --region $PRIMARY_REGION

wait_for_stack "${PROJECT_NAME}-app" $PRIMARY_REGION

# Step 5: Deploy Monitoring
echo ""
echo "Step 5: Deploying Monitoring and Alerts..."
aws cloudformation create-stack \
    --stack-name ${PROJECT_NAME}-monitoring \
    --template-body file://infrastructure/cloudformation/04-monitoring.yaml \
    --parameters \
        ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
        ParameterKey=AlertEmail,ParameterValue=$ALERT_EMAIL \
    --region $PRIMARY_REGION

wait_for_stack "${PROJECT_NAME}-monitoring" $PRIMARY_REGION

# Get outputs
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Getting stack outputs..."

REPO_URL=$(aws cloudformation describe-stacks \
    --stack-name ${PROJECT_NAME}-pipeline \
    --query 'Stacks[0].Outputs[?OutputKey==`RepositoryCloneUrlHttp`].OutputValue' \
    --output text \
    --region $PRIMARY_REGION)

API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name ${PROJECT_NAME}-app \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text \
    --region $PRIMARY_REGION)

echo ""
echo "📦 CodeCommit Repository: $REPO_URL"
echo "🚀 API Endpoint: $API_ENDPOINT"
echo ""
echo "Next Steps:"
echo "1. Configure git credentials for CodeCommit"
echo "2. Push your code to the repository"
echo "3. Monitor the pipeline in AWS Console"
echo ""
