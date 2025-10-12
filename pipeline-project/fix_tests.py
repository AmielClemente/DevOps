#!/usr/bin/env python3
"""
Script to fix remaining tests by adding DynamoDB mock
"""

import re

def fix_test_file():
    with open('tests/test_simple.py', 'r') as f:
        content = f.read()
    
    # Fix test_5_unit_environment_variables
    pattern1 = r'(def test_5_unit_environment_variables\(mock_environment, mock_cloudwatch, mock_dynamodb, mock_requests_success\):.*?with patch\.dict\(os\.environ, mock_environment\):\s+with patch\(\'boto3\.client\', return_value=mock_cloudwatch\):\s+with patch\(\'requests\.get\', return_value=mock_requests_success\):)'
    replacement1 = r'\1\n                with patch(\'boto3.resource\', return_value=mock_dynamodb):'
    
    # Fix functional tests - add DynamoDB mock
    functional_tests = [
        'test_2_functional_multi_website_monitoring',
        'test_3_functional_performance_measurement', 
        'test_4_functional_mixed_scenarios',
        'test_5_functional_complete_monitoring_cycle'
    ]
    
    for test_name in functional_tests:
        # Add DynamoDB mock to each functional test
        pattern = f'(def {test_name}\\(mock_environment, mock_cloudwatch, mock_dynamodb\\):.*?with patch\\.dict\\(os\\.environ, mock_environment\\):\\s+with patch\\(\'boto3\\.client\', return_value=mock_cloudwatch\\):)'
        replacement = r'\1\n            with patch(\'boto3.resource\', return_value=mock_dynamodb):'
        
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open('tests/test_simple.py', 'w') as f:
        f.write(content)
    
    print("Fixed remaining tests!")

if __name__ == "__main__":
    fix_test_file()

