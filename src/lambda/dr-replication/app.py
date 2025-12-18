import boto3
import json
import os
from datetime import datetime

def lambda_handler(event, context):
    """Replicate DynamoDB data to DR region"""
    
    primary_region = os.environ.get('PRIMARY_REGION', 'us-east-1')
    dr_region = os.environ.get('DR_REGION', 'us-west-2')
    table_name = os.environ.get('TABLE_NAME', 'DevOpsMetrics')
    
    try:
        # Get data from primary region
        primary_dynamodb = boto3.resource('dynamodb', region_name=primary_region)
        primary_table = primary_dynamodb.Table(table_name)
        
        # Scan primary table
        response = primary_table.scan()
        items = response.get('Items', [])
        
        # Replicate to DR region
        dr_dynamodb = boto3.resource('dynamodb', region_name=dr_region)
        dr_table = dr_dynamodb.Table(table_name)
        
        replicated_count = 0
        for item in items:
            dr_table.put_item(Item=item)
            replicated_count += 1
        
        result = {
            'status': 'success',
            'replicated_items': replicated_count,
            'timestamp': datetime.utcnow().isoformat(),
            'primary_region': primary_region,
            'dr_region': dr_region
        }
        
        # Log to CloudWatch
        print(json.dumps(result))
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        error_result = {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print(json.dumps(error_result))
        
        return {
            'statusCode': 500,
            'body': json.dumps(error_result)
        }
