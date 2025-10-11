import boto3
import json
import uuid
import time
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for CRUD API Gateway operations
    """
    try:
        # Get HTTP method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        
        logger.info(f"Processing {http_method} request to {path}")
        
        # Parse request body if present
        body = None
        if event.get('body'):
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError:
                return create_response(400, {"error": "Invalid JSON in request body"})
        
        # Route requests based on HTTP method and path
        if http_method == 'GET' and path == '/websites':
            return list_websites()
        elif http_method == 'GET' and path.startswith('/websites/'):
            website_id = path_parameters.get('id')
            if not website_id:
                return create_response(400, {"error": "Website ID is required"})
            return get_website(website_id)
        elif http_method == 'POST' and path == '/websites':
            return create_website(body)
        elif http_method == 'PUT' and path.startswith('/websites/'):
            website_id = path_parameters.get('id')
            if not website_id:
                return create_response(400, {"error": "Website ID is required"})
            return update_website(website_id, body)
        elif http_method == 'DELETE' and path.startswith('/websites/'):
            website_id = path_parameters.get('id')
            if not website_id:
                return create_response(400, {"error": "Website ID is required"})
            return delete_website(website_id)
        else:
            return create_response(405, {"error": f"Method {http_method} not allowed for {path}"})
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_response(500, {"error": "Internal server error"})

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create a standardized API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body)
    }

def get_table():
    """Get the DynamoDB table for website targets"""
    table_name = os.environ.get('TARGET_WEBSITES_TABLE') or os.environ.get('TARGET_TABLE')
    if not table_name:
        raise ValueError("TARGET_WEBSITES_TABLE or TARGET_TABLE environment variable not set")
    return dynamodb.Table(table_name)

def list_websites() -> Dict[str, Any]:
    """List all websites in the target list"""
    try:
        table = get_table()
        
        # Scan the table to get all websites
        response = table.scan()
        websites = response.get('Items', [])
        
        # Sort by created_at timestamp
        websites.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return create_response(200, {
            "websites": websites,
            "count": len(websites)
        })
        
    except Exception as e:
        logger.error(f"Error listing websites: {str(e)}")
        return create_response(500, {"error": "Failed to list websites"})

def get_website(website_id: str) -> Dict[str, Any]:
    """Get a specific website by ID"""
    try:
        table = get_table()
        
        response = table.get_item(Key={'id': website_id})
        
        if 'Item' not in response:
            return create_response(404, {"error": "Website not found"})
        
        return create_response(200, {
            "website": response['Item']
        })
        
    except Exception as e:
        logger.error(f"Error getting website {website_id}: {str(e)}")
        return create_response(500, {"error": "Failed to get website"})

def create_website(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a new website entry"""
    try:
        if not data:
            return create_response(400, {"error": "Request body is required"})
        
        # Validate required fields
        required_fields = ['url', 'name']
        for field in required_fields:
            if field not in data or not data[field]:
                return create_response(400, {"error": f"Field '{field}' is required"})
        
        # Validate URL format
        url = data['url']
        if not url.startswith(('http://', 'https://')):
            return create_response(400, {"error": "URL must start with http:// or https://"})
        
        # Additional URL validation
        try:
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            if not parsed.netloc:
                return create_response(400, {"error": "Invalid URL format"})
        except Exception:
            return create_response(400, {"error": "Invalid URL format"})
        
        # Generate unique ID and timestamps
        website_id = str(uuid.uuid4())
        current_time = datetime.utcnow().isoformat()
        
        # Prepare website data
        website_data = {
            'id': website_id,
            'url': url,
            'name': data['name'],
            'description': data.get('description', ''),
            'enabled': data.get('enabled', True),
            'check_interval': data.get('check_interval', 300),  # 5 minutes default
            'timeout': data.get('timeout', 30),
            'expected_status': data.get('expected_status', 200),
            'created_at': current_time,
            'updated_at': current_time
        }
        
        table = get_table()
        table.put_item(Item=website_data)
        
        logger.info(f"Created website {website_id}: {url}")
        
        return create_response(201, {
            "message": "Website created successfully",
            "website": website_data
        })
        
    except Exception as e:
        logger.error(f"Error creating website: {str(e)}")
        return create_response(500, {"error": "Failed to create website"})

def update_website(website_id: str, data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Update an existing website entry"""
    try:
        if not data:
            return create_response(400, {"error": "Request body is required"})
        
        table = get_table()
        
        # Check if website exists
        response = table.get_item(Key={'id': website_id})
        if 'Item' not in response:
            return create_response(404, {"error": "Website not found"})
        
        existing_website = response['Item']
        
        # Prepare update expression
        update_expression = "SET updated_at = :updated_at"
        expression_values = {':updated_at': datetime.utcnow().isoformat()}
        
        # Update fields that are provided
        updatable_fields = ['name', 'description', 'enabled', 'check_interval', 'timeout', 'expected_status']
        for field in updatable_fields:
            if field in data:
                update_expression += f", {field} = :{field}"
                expression_values[f':{field}'] = data[field]
        
        # Special handling for URL (validate format)
        if 'url' in data:
            url = data['url']
            if not url.startswith(('http://', 'https://')):
                return create_response(400, {"error": "URL must start with http:// or https://"})
            update_expression += ", url = :url"
            expression_values[':url'] = url
        
        # Perform update
        table.update_item(
            Key={'id': website_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues='ALL_NEW'
        )
        
        # Get updated item
        response = table.get_item(Key={'id': website_id})
        updated_website = response['Item']
        
        logger.info(f"Updated website {website_id}")
        
        return create_response(200, {
            "message": "Website updated successfully",
            "website": updated_website
        })
        
    except Exception as e:
        logger.error(f"Error updating website {website_id}: {str(e)}")
        return create_response(500, {"error": "Failed to update website"})

def delete_website(website_id: str) -> Dict[str, Any]:
    """Delete a website entry"""
    try:
        table = get_table()
        
        # Check if website exists
        response = table.get_item(Key={'id': website_id})
        if 'Item' not in response:
            return create_response(404, {"error": "Website not found"})
        
        # Delete the website
        table.delete_item(Key={'id': website_id})
        
        logger.info(f"Deleted website {website_id}")
        
        return create_response(200, {
            "message": "Website deleted successfully",
            "website_id": website_id
        })
        
    except Exception as e:
        logger.error(f"Error deleting website {website_id}: {str(e)}")
        return create_response(500, {"error": "Failed to delete website"})
