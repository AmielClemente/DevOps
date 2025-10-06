"""
CRUD API Handler for Target Websites
Handles Create, Read, Update, Delete operations for target websites
"""
import json
import boto3
import uuid
import os
from datetime import datetime
from decimal import Decimal
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = None

def convert_decimals(obj):
    """Convert Decimal objects to int/float for JSON serialization"""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    return obj

def lambda_handler(event, context):
    """
    Lambda handler for CRUD operations on target websites
    """
    global table_name
    if not table_name:
        table_name = os.environ.get('TARGET_TABLE')
    
    if not table_name:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'TARGET_TABLE environment variable not set'})
        }
    
    table = dynamodb.Table(table_name)
    http_method = event['httpMethod']
    path_parameters = event.get('pathParameters', {})
    body = event.get('body', '{}')
    
    try:
        if http_method == 'GET':
            if path_parameters and 'id' in path_parameters:
                # GET /websites/{id} - Get specific website
                return get_website(table, path_parameters['id'])
            else:
                # GET /websites - List all websites
                return list_websites(table)
        
        elif http_method == 'POST':
            # POST /websites - Create new website
            return create_website(table, json.loads(body))
        
        elif http_method == 'PUT':
            # PUT /websites/{id} - Update website
            if not path_parameters or 'id' not in path_parameters:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Website ID is required for update'})
                }
            return update_website(table, path_parameters['id'], json.loads(body))
        
        elif http_method == 'DELETE':
            # DELETE /websites/{id} - Delete website
            if not path_parameters or 'id' not in path_parameters:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Website ID is required for deletion'})
                }
            return delete_website(table, path_parameters['id'])
        
        else:
            return {
                'statusCode': 405,
                'body': json.dumps({'error': f'Method {http_method} not allowed'})
            }
    
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'DynamoDB error: {str(e)}'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

def create_website(table, data):
    """Create a new website entry"""
    # Validate required fields
    if 'url' not in data:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'URL is required'})
        }
    
    # Generate unique ID
    website_id = str(uuid.uuid4())
    
    # Prepare item
    item = {
        'id': website_id,
        'url': data['url'],
        'name': data.get('name', data['url']),
        'description': data.get('description', ''),
        'enabled': data.get('enabled', True),
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    # Add optional fields
    if 'check_interval' in data:
        item['check_interval'] = data['check_interval']
    if 'timeout' in data:
        item['timeout'] = data['timeout']
    if 'expected_status' in data:
        item['expected_status'] = data['expected_status']
    
    try:
        table.put_item(Item=item)
        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Website created successfully',
                'website': item
            })
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Failed to create website: {str(e)}'})
        }

def get_website(table, website_id):
    """Get a specific website by ID"""
    try:
        response = table.get_item(Key={'id': website_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Website not found'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({'website': convert_decimals(response['Item'])})
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Failed to get website: {str(e)}'})
        }

def list_websites(table):
    """List all websites"""
    try:
        response = table.scan()
        
        websites = response.get('Items', [])
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'websites': convert_decimals(websites),
                'count': len(websites)
            })
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Failed to list websites: {str(e)}'})
        }

def update_website(table, website_id, data):
    """Update an existing website"""
    try:
        # First check if website exists
        response = table.get_item(Key={'id': website_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Website not found'})
            }
        
        # Prepare update expression with attribute names for reserved keywords
        update_expression = "SET updated_at = :updated_at"
        expression_values = {':updated_at': datetime.utcnow().isoformat()}
        expression_names = {}
        
        # Add fields to update
        allowed_fields = ['url', 'name', 'description', 'enabled', 'check_interval', 'timeout', 'expected_status']
        
        for field in allowed_fields:
            if field in data:
                # Use attribute names for reserved keywords
                attr_name = f"#{field}" if field in ['name'] else field
                if field in ['name']:
                    expression_names[attr_name] = field
                update_expression += f", {attr_name} = :{field}"
                expression_values[f':{field}'] = data[field]
        
        # Perform update
        update_params = {
            'Key': {'id': website_id},
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_values,
            'ReturnValues': 'ALL_NEW'
        }
        
        if expression_names:
            update_params['ExpressionAttributeNames'] = expression_names
            
        table.update_item(**update_params)
        
        # Get updated item
        updated_response = table.get_item(Key={'id': website_id})
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Website updated successfully',
                'website': convert_decimals(updated_response['Item'])
            })
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Failed to update website: {str(e)}'})
        }

def delete_website(table, website_id):
    """Delete a website"""
    try:
        # First check if website exists
        response = table.get_item(Key={'id': website_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Website not found'})
            }
        
        # Delete the item
        table.delete_item(Key={'id': website_id})
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Website deleted successfully'})
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Failed to delete website: {str(e)}'})
        }
