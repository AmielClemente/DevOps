import pytest
import json
import boto3
from moto import mock_aws
from unittest.mock import patch, MagicMock
import os
import sys

# Add the lambda directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'crud_api'))

from crud_handler import lambda_handler, create_website, get_website, list_websites, update_website, delete_website

class TestCRUDAPI:
    """Test suite for CRUD API Lambda function"""
    
    @pytest.fixture
    def mock_event_get_websites(self):
        """Mock API Gateway event for GET /websites"""
        return {
            'httpMethod': 'GET',
            'path': '/websites',
            'pathParameters': None,
            'queryStringParameters': None,
            'body': None
        }
    
    @pytest.fixture
    def mock_event_get_website(self):
        """Mock API Gateway event for GET /websites/{id}"""
        return {
            'httpMethod': 'GET',
            'path': '/websites/test-id',
            'pathParameters': {'id': 'test-id'},
            'queryStringParameters': None,
            'body': None
        }
    
    @pytest.fixture
    def mock_event_create_website(self):
        """Mock API Gateway event for POST /websites"""
        return {
            'httpMethod': 'POST',
            'path': '/websites',
            'pathParameters': None,
            'queryStringParameters': None,
            'body': json.dumps({
                'url': 'https://example.com',
                'name': 'Example Website',
                'description': 'A test website',
                'enabled': True,
                'check_interval': 300
            })
        }
    
    @pytest.fixture
    def mock_event_update_website(self):
        """Mock API Gateway event for PUT /websites/{id}"""
        return {
            'httpMethod': 'PUT',
            'path': '/websites/test-id',
            'pathParameters': {'id': 'test-id'},
            'queryStringParameters': None,
            'body': json.dumps({
                'name': 'Updated Website',
                'enabled': False
            })
        }
    
    @pytest.fixture
    def mock_event_delete_website(self):
        """Mock API Gateway event for DELETE /websites/{id}"""
        return {
            'httpMethod': 'DELETE',
            'path': '/websites/test-id',
            'pathParameters': {'id': 'test-id'},
            'queryStringParameters': None,
            'body': None
        }
    
    @pytest.fixture
    def sample_website_data(self):
        """Sample website data for testing"""
        return {
            'id': 'test-id',
            'url': 'https://example.com',
            'name': 'Example Website',
            'description': 'A test website',
            'enabled': True,
            'check_interval': 300,
            'timeout': 30,
            'expected_status': 200,
            'created_at': '2024-01-01T00:00:00.000Z',
            'updated_at': '2024-01-01T00:00:00.000Z'
        }

    @mock_aws
    def test_create_website_success(self, mock_event_create_website):
        """Test successful website creation"""
        # Create mock DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        with patch.dict(os.environ, {'TARGET_WEBSITES_TABLE': 'test-table'}):
            response = lambda_handler(mock_event_create_website, {})
            
            assert response['statusCode'] == 201
            body = json.loads(response['body'])
            assert body['message'] == 'Website created successfully'
            assert 'website' in body
            assert body['website']['url'] == 'https://example.com'
            assert body['website']['name'] == 'Example Website'

    @mock_aws
    def test_create_website_missing_required_fields(self):
        """Test website creation with missing required fields"""
        event = {
            'httpMethod': 'POST',
            'path': '/websites',
            'pathParameters': None,
            'queryStringParameters': None,
            'body': json.dumps({
                'name': 'Example Website'
                # Missing 'url' field
            })
        }
        
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        with patch.dict(os.environ, {'TARGET_WEBSITES_TABLE': 'test-table'}):
            response = lambda_handler(event, {})
            
            assert response['statusCode'] == 400
            body = json.loads(response['body'])
            assert 'error' in body
            assert 'required' in body['error']

    @mock_aws
    def test_create_website_invalid_url(self):
        """Test website creation with invalid URL"""
        event = {
            'httpMethod': 'POST',
            'path': '/websites',
            'pathParameters': None,
            'queryStringParameters': None,
            'body': json.dumps({
                'url': 'invalid-url',
                'name': 'Example Website'
            })
        }
        
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        with patch.dict(os.environ, {'TARGET_WEBSITES_TABLE': 'test-table'}):
            response = lambda_handler(event, {})
            
            assert response['statusCode'] == 400
            body = json.loads(response['body'])
            assert 'error' in body
            assert 'http' in body['error'].lower()

    @mock_aws
    def test_list_websites_success(self, mock_event_get_websites, sample_website_data):
        """Test successful website listing"""
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Add test data
        table.put_item(Item=sample_website_data)
        
        with patch.dict(os.environ, {'TARGET_WEBSITES_TABLE': 'test-table'}):
            response = lambda_handler(mock_event_get_websites, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert 'websites' in body
            assert 'count' in body
            assert body['count'] == 1
            assert len(body['websites']) == 1

    @mock_aws
    def test_get_website_success(self, mock_event_get_website, sample_website_data):
        """Test successful website retrieval"""
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Add test data
        table.put_item(Item=sample_website_data)
        
        with patch.dict(os.environ, {'TARGET_WEBSITES_TABLE': 'test-table'}):
            response = lambda_handler(mock_event_get_website, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert 'website' in body
            assert body['website']['id'] == 'test-id'
            assert body['website']['url'] == 'https://example.com'

    @mock_aws
    def test_get_website_not_found(self, mock_event_get_website):
        """Test website retrieval when website doesn't exist"""
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        with patch.dict(os.environ, {'TARGET_WEBSITES_TABLE': 'test-table'}):
            response = lambda_handler(mock_event_get_website, {})
            
            assert response['statusCode'] == 404
            body = json.loads(response['body'])
            assert 'error' in body
            assert 'not found' in body['error'].lower()

    @mock_aws
    def test_update_website_success(self, mock_event_update_website, sample_website_data):
        """Test successful website update"""
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Add test data
        table.put_item(Item=sample_website_data)
        
        with patch.dict(os.environ, {'TARGET_WEBSITES_TABLE': 'test-table'}):
            response = lambda_handler(mock_event_update_website, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['message'] == 'Website updated successfully'
            assert body['website']['name'] == 'Updated Website'
            assert body['website']['enabled'] == False

    @mock_aws
    def test_delete_website_success(self, mock_event_delete_website, sample_website_data):
        """Test successful website deletion"""
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Add test data
        table.put_item(Item=sample_website_data)
        
        with patch.dict(os.environ, {'TARGET_WEBSITES_TABLE': 'test-table'}):
            response = lambda_handler(mock_event_delete_website, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['message'] == 'Website deleted successfully'
            assert body['website_id'] == 'test-id'

    def test_invalid_http_method(self):
        """Test handling of invalid HTTP methods"""
        event = {
            'httpMethod': 'PATCH',
            'path': '/websites',
            'pathParameters': None,
            'queryStringParameters': None,
            'body': None
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 405
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'not allowed' in body['error']

    def test_invalid_json_body(self):
        """Test handling of invalid JSON in request body"""
        event = {
            'httpMethod': 'POST',
            'path': '/websites',
            'pathParameters': None,
            'queryStringParameters': None,
            'body': 'invalid json'
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'Invalid JSON' in body['error']

    @mock_aws
    def test_dynamodb_performance_read(self, sample_website_data):
        """Test DynamoDB read performance"""
        import time
        
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Add test data
        table.put_item(Item=sample_website_data)
        
        with patch.dict(os.environ, {'TARGET_WEBSITES_TABLE': 'test-table'}):
            start_time = time.time()
            response = get_website('test-id')
            end_time = time.time()
            
            # Should complete within 100ms (0.1 seconds)
            assert (end_time - start_time) < 0.1
            assert response['statusCode'] == 200

    @mock_aws
    def test_dynamodb_performance_write(self):
        """Test DynamoDB write performance"""
        import time
        
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        with patch.dict(os.environ, {'TARGET_WEBSITES_TABLE': 'test-table'}):
            start_time = time.time()
            response = create_website({
                'url': 'https://example.com',
                'name': 'Test Website'
            })
            end_time = time.time()
            
            # Should complete within 200ms (0.2 seconds)
            assert (end_time - start_time) < 0.2
            assert response['statusCode'] == 201

    def test_cors_headers(self, mock_event_get_websites):
        """Test that CORS headers are included in responses"""
        with patch.dict(os.environ, {'TARGET_WEBSITES_TABLE': 'test-table'}):
            with mock_aws():
                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                table = dynamodb.create_table(
                    TableName='test-table',
                    KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                    AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                    BillingMode='PAY_PER_REQUEST'
                )
                
                response = lambda_handler(mock_event_get_websites, {})
                
                assert 'headers' in response
                assert 'Access-Control-Allow-Origin' in response['headers']
                assert response['headers']['Access-Control-Allow-Origin'] == '*'
                assert 'Access-Control-Allow-Methods' in response['headers']