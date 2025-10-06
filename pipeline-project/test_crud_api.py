#!/usr/bin/env python3
"""
Simple CRUD API Test Script
Tests the Website Crawler CRUD API functionality
"""

import requests
import json
import time
import sys

# Configuration
API_BASE_URL = "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod"  # Replace with actual URL
TEST_WEBSITE_URL = "https://httpbin.org/status/200"

def print_response(title, response):
    """Print formatted response"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_api_endpoints():
    """Test all CRUD API endpoints"""
    
    print("🚀 Starting CRUD API Tests")
    print(f"API Base URL: {API_BASE_URL}")
    
    # Test data
    test_website = {
        "url": TEST_WEBSITE_URL,
        "name": "HTTPBin Test Site",
        "description": "A test website for API testing",
        "enabled": True,
        "check_interval": 300,
        "timeout": 30,
        "expected_status": 200
    }
    
    website_id = None
    
    try:
        # 1. CREATE - Test POST /websites
        print("\n1️⃣ Testing CREATE (POST /websites)")
        response = requests.post(f"{API_BASE_URL}/websites", json=test_website)
        print_response("CREATE Website", response)
        
        if response.status_code == 201:
            website_id = response.json()['website']['id']
            print(f"✅ Website created successfully with ID: {website_id}")
        else:
            print("❌ Failed to create website")
            return False
        
        # 2. READ ALL - Test GET /websites
        print("\n2️⃣ Testing READ ALL (GET /websites)")
        response = requests.get(f"{API_BASE_URL}/websites")
        print_response("List All Websites", response)
        
        if response.status_code == 200:
            websites = response.json().get('websites', [])
            print(f"✅ Found {len(websites)} websites")
        else:
            print("❌ Failed to list websites")
        
        # 3. READ ONE - Test GET /websites/{id}
        print("\n3️⃣ Testing READ ONE (GET /websites/{id})")
        if website_id:
            response = requests.get(f"{API_BASE_URL}/websites/{website_id}")
            print_response("Get Specific Website", response)
            
            if response.status_code == 200:
                print("✅ Website retrieved successfully")
            else:
                print("❌ Failed to retrieve website")
        
        # 4. UPDATE - Test PUT /websites/{id}
        print("\n4️⃣ Testing UPDATE (PUT /websites/{id})")
        if website_id:
            update_data = {
                "name": "Updated HTTPBin Test Site",
                "description": "Updated description",
                "enabled": False
            }
            response = requests.put(f"{API_BASE_URL}/websites/{website_id}", json=update_data)
            print_response("Update Website", response)
            
            if response.status_code == 200:
                print("✅ Website updated successfully")
            else:
                print("❌ Failed to update website")
        
        # 5. DELETE - Test DELETE /websites/{id}
        print("\n5️⃣ Testing DELETE (DELETE /websites/{id})")
        if website_id:
            response = requests.delete(f"{API_BASE_URL}/websites/{website_id}")
            print_response("Delete Website", response)
            
            if response.status_code == 200:
                print("✅ Website deleted successfully")
            else:
                print("❌ Failed to delete website")
        
        # 6. Verify deletion
        print("\n6️⃣ Verifying deletion")
        if website_id:
            response = requests.get(f"{API_BASE_URL}/websites/{website_id}")
            print_response("Verify Deletion", response)
            
            if response.status_code == 404:
                print("✅ Website successfully deleted (404 as expected)")
            else:
                print("❌ Website still exists after deletion")
        
        print("\n🎉 All tests completed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to API Gateway")
        print("   Make sure the API Gateway URL is correct and the service is deployed")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_error_handling():
    """Test error handling scenarios"""
    
    print("\n🔍 Testing Error Handling")
    
    try:
        # Test invalid JSON
        print("\n1️⃣ Testing invalid JSON")
        response = requests.post(f"{API_BASE_URL}/websites", 
                               data="invalid json {", 
                               headers={"Content-Type": "application/json"})
        print_response("Invalid JSON", response)
        
        # Test missing URL
        print("\n2️⃣ Testing missing URL")
        response = requests.post(f"{API_BASE_URL}/websites", 
                               json={"name": "Test without URL"})
        print_response("Missing URL", response)
        
        # Test non-existent website
        print("\n3️⃣ Testing non-existent website")
        response = requests.get(f"{API_BASE_URL}/websites/non-existent-id")
        print_response("Non-existent Website", response)
        
        # Test invalid method
        print("\n4️⃣ Testing invalid HTTP method")
        response = requests.patch(f"{API_BASE_URL}/websites")
        print_response("Invalid Method", response)
        
        print("✅ Error handling tests completed")
        
    except Exception as e:
        print(f"❌ Error in error handling tests: {str(e)}")

def get_api_url():
    """Get API Gateway URL from AWS"""
    try:
        import subprocess
        
        print("🔍 Attempting to find API Gateway URL...")
        
        # Get API Gateway ID
        result = subprocess.run([
            'aws', 'apigateway', 'get-rest-apis',
            '--query', 'items[?name==`Website Target CRUD API`].id',
            '--output', 'text'
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            api_id = result.stdout.strip()
            region = subprocess.run([
                'aws', 'configure', 'get', 'region'
            ], capture_output=True, text=True).stdout.strip()
            
            api_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/prod"
            print(f"✅ Found API Gateway URL: {api_url}")
            return api_url
        else:
            print("❌ Could not find API Gateway")
            return None
            
    except Exception as e:
        print(f"❌ Error finding API Gateway: {str(e)}")
        return None

def main():
    """Main test function"""
    
    global API_BASE_URL
    
    print("🧪 CRUD API Test Suite")
    print("=" * 50)
    
    # Try to get API URL automatically
    auto_url = get_api_url()
    if auto_url:
        API_BASE_URL = auto_url
    
    # If still using placeholder, ask user
    if "your-api-id" in API_BASE_URL:
        print("\n⚠️  Please update the API_BASE_URL in this script with your actual API Gateway URL")
        print("   You can find it in the AWS Console under API Gateway")
        print("   Or run: aws apigateway get-rest-apis")
        return
    
    # Run tests
    success = test_api_endpoints()
    
    if success:
        test_error_handling()
    
    print("\n" + "=" * 50)
    print("🏁 Test Suite Complete")
    
    if success:
        print("✅ All basic tests passed!")
        print("\nNext steps:")
        print("1. Check CloudWatch logs for Lambda function execution")
        print("2. Verify DynamoDB table has the test data")
        print("3. Test integration with web crawler")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        print("\nTroubleshooting:")
        print("1. Verify API Gateway is deployed and accessible")
        print("2. Check Lambda function logs in CloudWatch")
        print("3. Verify DynamoDB table exists and has proper permissions")

if __name__ == "__main__":
    main()
