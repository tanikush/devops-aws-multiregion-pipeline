import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../lambda/api-handler')))

def test_health_check():
    """Test health check endpoint"""
    from app import health_check
    
    response = health_check()
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['status'] == 'healthy'
    print("✓ Health check test passed")

def test_response_format():
    """Test response format"""
    from app import response
    
    result = response(200, {'test': 'data'})
    
    assert result['statusCode'] == 200
    assert 'headers' in result
    assert result['headers']['Content-Type'] == 'application/json'
    print("✓ Response format test passed")

if __name__ == '__main__':
    print("Running tests...")
    test_health_check()
    test_response_format()
    print("\nAll tests passed! ✓")
