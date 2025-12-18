import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'DevOpsMetrics')

def lambda_handler(event, context):
    """Main API handler for DevOps monitoring"""
    
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    
    try:
        if http_method == 'GET' and path == '/health':
            return health_check()
        
        elif http_method == 'GET' and path == '/metrics':
            return get_metrics()
        
        elif http_method == 'POST' and path == '/metrics':
            return post_metric(event)
        
        else:
            return response(404, {'error': 'Not found'})
    
    except Exception as e:
        return response(500, {'error': str(e)})

def health_check():
    """Health check endpoint"""
    return response(200, {
        'status': 'healthy',
        'region': os.environ.get('AWS_REGION', 'unknown'),
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'DevOps Monitor API'
    })

def get_metrics():
    """Get all deployment metrics"""
    try:
        table = dynamodb.Table(table_name)
        result = table.scan(Limit=50)
        
        return response(200, {
            'metrics': result.get('Items', []),
            'count': len(result.get('Items', []))
        })
    except Exception as e:
        return response(500, {'error': f'Database error: {str(e)}'})

def post_metric(event):
    """Store new deployment metric"""
    try:
        body = json.loads(event.get('body', '{}'))
        
        table = dynamodb.Table(table_name)
        item = {
            'id': f"{datetime.utcnow().timestamp()}",
            'timestamp': datetime.utcnow().isoformat(),
            'deployment_id': body.get('deployment_id', 'unknown'),
            'status': body.get('status', 'unknown'),
            'duration': body.get('duration', 0),
            'region': os.environ.get('AWS_REGION', 'unknown')
        }
        
        table.put_item(Item=item)
        
        return response(201, {
            'message': 'Metric stored successfully',
            'item': item
        })
    except Exception as e:
        return response(500, {'error': f'Failed to store metric: {str(e)}'})

def response(status_code, body):
    """Standard API response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }
