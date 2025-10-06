"""
Test CRUD API operations for Target Websites
Tests Create, Read, Update, Delete operations and DynamoDB performance
"""
import pytest
import json
import boto3
from unittest.mock import Mock, patch, MagicMock
from moto import mock_dynamodb
import time

# Import the CRUD handler
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda', 'crud_api'))
from crud_handler import lambda_handler, create_website, get_website, list_websites, update_website, delete_website

class TestCRUDAPI:
    """Test class for CRUD API operations"""
    
    @pytest.fixture
    def mock_context(self):
        """Mock Lambda context"""
        context = Mock()
        context.environment = {'TARGET_TABLE': 'test-target-websites'}
        return context
    
    @pytest.fixture
    def sample_website_data(self):
        """Sample website data for testing"""
        return {
            'url': 'https://example.com',
            'name': 'Example Website',
            'description': 'A test website',
            'enabled': True,
            'check_interval': 300,
            'timeout': 30,
            'expected_status': 200
        }
    
    @pytest.fixture
    def mock_event_get_all(self):
        """Mock event for GET all websites"""
        return {
            'httpMethod': 'GET',
            'pathParameters': None,
            'body': None
        }
    
    @pytest.fixture
    def mock_event_get_one(self):
        """Mock event for GET specific website"""
        return {
            'httpMethod': 'GET',
            'pathParameters': {'id': 'test-id-123'},
            'body': None
        }
    
    @pytest.fixture
    def mock_event_post(self):
        """Mock event for POST (create) website"""
        return {
            'httpMethod': 'POST',
            'pathParameters': None,
            'body': json.dumps({
                'url': 'https://example.com',
                'name': 'Example Website',
                'description': 'A test website',
                'enabled': True
            })
        }
    
    @pytest.fixture
    def mock_event_put(self):
        """Mock event for PUT (update) website"""
        return {
            'httpMethod': 'PUT',
            'pathParameters': {'id': 'test-id-123'},
            'body': json.dumps({
                'name': 'Updated Website Name',
                'description': 'Updated description'
            })
        }
    
    @pytest.fixture
    def mock_event_delete(self):
        """Mock event for DELETE website"""
        return {
            'httpMethod': 'DELETE',
            'pathParameters': {'id': 'test-id-123'},
            'body': None
        }

    def test_create_website_success(self, mock_context, sample_website_data):
        """Test successful website creation"""
        with mock_dynamodb():
            # Create mock table
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.create_table(
                TableName='test-target-websites',
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Test create_website function
            result = create_website(table, sample_website_data)
            
            assert result['statusCode'] == 201
            response_body = json.loads(result['body'])
            assert response_body['message'] == 'Website created successfully'
            assert 'website' in response_body
            assert response_body['website']['url'] == sample_website_data['url']
            assert 'id' in response_body['website']

    def test_create_website_missing_url(self, mock_context):
        """Test website creation with missing URL"""
        with mock_dynamodb():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.create_table(
                TableName='test-target-websites',
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            
            result = create_website(table, {'name': 'Test Website'})
            
            assert result['statusCode'] == 400
            response_body = json.loads(result['body'])
            assert 'error' in response_body
            assert 'URL is required' in response_body['error']

    def test_get_website_success(self, mock_context):
        """Test successful website retrieval"""
        with mock_dynamodb():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.create_table(
                TableName='test-target-websites',
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Insert test data
            test_id = 'test-id-123'
            table.put_item(Item={
                'id': test_id,
                'url': 'https://example.com',
                'name': 'Test Website'
            })
            
            result = get_website(table, test_id)
            
            assert result['statusCode'] == 200
            response_body = json.loads(result['body'])
            assert 'website' in response_body
            assert response_body['website']['id'] == test_id

    def test_get_website_not_found(self, mock_context):
        """Test website retrieval when website doesn't exist"""
        with mock_dynamodb():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.create_table(
                TableName='test-target-websites',
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            
            result = get_website(table, 'non-existent-id')
            
            assert result['statusCode'] == 404
            response_body = json.loads(result['body'])
            assert 'error' in response_body
            assert 'not found' in response_body['error']

    def test_list_websites_success(self, mock_context):
        """Test successful website listing"""
        with mock_dynamodb():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.create_table(
                TableName='test-target-websites',
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Insert test data
            table.put_item(Item={'id': 'id1', 'url': 'https://site1.com', 'name': 'Site 1'})
            table.put_item(Item={'id': 'id2', 'url': 'https://site2.com', 'name': 'Site 2'})
            
            result = list_websites(table)
            
            assert result['statusCode'] == 200
            response_body = json.loads(result['body'])
            assert 'websites' in response_body
            assert 'count' in response_body
            assert response_body['count'] == 2
            assert len(response_body['websites']) == 2

    def test_update_website_success(self, mock_context):
        """Test successful website update"""
        with mock_dynamodb():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.create_table(
                TableName='test-target-websites',
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Insert test data
            test_id = 'test-id-123'
            table.put_item(Item={
                'id': test_id,
                'url': 'https://example.com',
                'name': 'Original Name'
            })
            
            update_data = {'name': 'Updated Name', 'description': 'New description'}
            result = update_website(table, test_id, update_data)
            
            assert result['statusCode'] == 200
            response_body = json.loads(result['body'])
            assert response_body['message'] == 'Website updated successfully'
            assert response_body['website']['name'] == 'Updated Name'

    def test_delete_website_success(self, mock_context):
        """Test successful website deletion"""
        with mock_dynamodb():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.create_table(
                TableName='test-target-websites',
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Insert test data
            test_id = 'test-id-123'
            table.put_item(Item={
                'id': test_id,
                'url': 'https://example.com',
                'name': 'Test Website'
            })
            
            result = delete_website(table, test_id)
            
            assert result['statusCode'] == 200
            response_body = json.loads(result['body'])
            assert response_body['message'] == 'Website deleted successfully'

    def test_lambda_handler_get_all(self, mock_context, mock_event_get_all):
        """Test Lambda handler for GET all websites"""
        with mock_dynamodb():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.create_table(
                TableName='test-target-websites',
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            
            with patch('crud_handler.dynamodb') as mock_dynamodb_resource:
                mock_dynamodb_resource.Table.return_value = table
                result = lambda_handler(mock_event_get_all, mock_context)
                
                assert result['statusCode'] == 200
                response_body = json.loads(result['body'])
                assert 'websites' in response_body

    def test_lambda_handler_post(self, mock_context, mock_event_post):
        """Test Lambda handler for POST (create) website"""
        with mock_dynamodb():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.create_table(
                TableName='test-target-websites',
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            
            with patch('crud_handler.dynamodb') as mock_dynamodb_resource:
                mock_dynamodb_resource.Table.return_value = table
                result = lambda_handler(mock_event_post, mock_context)
                
                assert result['statusCode'] == 201
                response_body = json.loads(result['body'])
                assert response_body['message'] == 'Website created successfully'

    def test_dynamodb_performance_read(self, mock_context):
        """Test DynamoDB read performance"""
        with mock_dynamodb():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.create_table(
                TableName='test-target-websites',
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Insert test data
            test_id = 'perf-test-id'
            table.put_item(Item={
                'id': test_id,
                'url': 'https://performance-test.com',
                'name': 'Performance Test Website'
            })
            
            # Measure read time
            start_time = time.time()
            result = get_website(table, test_id)
            end_time = time.time()
            
            read_time = end_time - start_time
            
            assert result['statusCode'] == 200
            assert read_time < 1.0  # Should complete within 1 second
            print(f"DynamoDB read time: {read_time:.4f} seconds")

    def test_dynamodb_performance_write(self, mock_context, sample_website_data):
        """Test DynamoDB write performance"""
        with mock_dynamodb():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.create_table(
                TableName='test-target-websites',
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Measure write time
            start_time = time.time()
            result = create_website(table, sample_website_data)
            end_time = time.time()
            
            write_time = end_time - start_time
            
            assert result['statusCode'] == 201
            assert write_time < 1.0  # Should complete within 1 second
            print(f"DynamoDB write time: {write_time:.4f} seconds")

    def test_invalid_json_body(self, mock_context):
        """Test handling of invalid JSON in request body"""
        invalid_event = {
            'httpMethod': 'POST',
            'pathParameters': None,
            'body': 'invalid json {'
        }
        
        with mock_dynamodb():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.create_table(
                TableName='test-target-websites',
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            
            with patch('crud_handler.dynamodb') as mock_dynamodb_resource:
                mock_dynamodb_resource.Table.return_value = table
                result = lambda_handler(invalid_event, mock_context)
                
                assert result['statusCode'] == 400
                response_body = json.loads(result['body'])
                assert 'error' in response_body
                assert 'Invalid JSON' in response_body['error']

    def test_method_not_allowed(self, mock_context):
        """Test handling of unsupported HTTP methods"""
        invalid_event = {
            'httpMethod': 'PATCH',
            'pathParameters': None,
            'body': None
        }
        
        with mock_dynamodb():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.create_table(
                TableName='test-target-websites',
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            
            with patch('crud_handler.dynamodb') as mock_dynamodb_resource:
                mock_dynamodb_resource.Table.return_value = table
                result = lambda_handler(invalid_event, mock_context)
                
                assert result['statusCode'] == 405
                response_body = json.loads(result['body'])
                assert 'error' in response_body
                assert 'not allowed' in response_body['error']
