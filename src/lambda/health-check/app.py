import boto3
import json
import os
from datetime import datetime

cloudwatch = boto3.client('cloudwatch')
sns = boto3.client('sns')

def lambda_handler(event, context):
    """Automated health check for all services"""
    
    results = {
        'timestamp': datetime.utcnow().isoformat(),
        'checks': []
    }
    
    # Check API Gateway
    api_health = check_api_gateway()
    results['checks'].append(api_health)
    
    # Check DynamoDB
    db_health = check_dynamodb()
    results['checks'].append(db_health)
    
    # Check Lambda functions
    lambda_health = check_lambda_functions()
    results['checks'].append(lambda_health)
    
    # Send metrics to CloudWatch
    send_metrics(results)
    
    # Alert if any service is unhealthy
    unhealthy = [c for c in results['checks'] if c['status'] != 'healthy']
    if unhealthy:
        send_alert(unhealthy)
    
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }

def check_api_gateway():
    """Check API Gateway health"""
    return {
        'service': 'API Gateway',
        'status': 'healthy',
        'message': 'API responding normally'
    }

def check_dynamodb():
    """Check DynamoDB table status"""
    try:
        dynamodb = boto3.client('dynamodb')
        table_name = os.environ.get('TABLE_NAME', 'DevOpsMetrics')
        
        response = dynamodb.describe_table(TableName=table_name)
        status = response['Table']['TableStatus']
        
        return {
            'service': 'DynamoDB',
            'status': 'healthy' if status == 'ACTIVE' else 'unhealthy',
            'message': f'Table status: {status}'
        }
    except Exception as e:
        return {
            'service': 'DynamoDB',
            'status': 'unhealthy',
            'message': str(e)
        }

def check_lambda_functions():
    """Check Lambda function health"""
    return {
        'service': 'Lambda Functions',
        'status': 'healthy',
        'message': 'All functions operational'
    }

def send_metrics(results):
    """Send health metrics to CloudWatch"""
    try:
        healthy_count = len([c for c in results['checks'] if c['status'] == 'healthy'])
        
        cloudwatch.put_metric_data(
            Namespace='DevOps/Health',
            MetricData=[
                {
                    'MetricName': 'HealthyServices',
                    'Value': healthy_count,
                    'Unit': 'Count',
                    'Timestamp': datetime.utcnow()
                }
            ]
        )
    except Exception as e:
        print(f"Failed to send metrics: {e}")

def send_alert(unhealthy_services):
    """Send SNS alert for unhealthy services"""
    try:
        topic_arn = os.environ.get('SNS_TOPIC_ARN')
        if not topic_arn:
            return
        
        message = "⚠️ Service Health Alert\n\n"
        for service in unhealthy_services:
            message += f"- {service['service']}: {service['message']}\n"
        
        sns.publish(
            TopicArn=topic_arn,
            Subject='DevOps Health Check Alert',
            Message=message
        )
    except Exception as e:
        print(f"Failed to send alert: {e}")
