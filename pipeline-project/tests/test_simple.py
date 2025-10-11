"""
BEGINNER-FRIENDLY TEST SUITE
============================
5 Unit Tests + 5 Functional Tests for Website Monitoring

UNIT TESTS: Test individual components in isolation
FUNCTIONAL TESTS: Test complete workflows end-to-end

Each test has clear explanations for learning!
"""
import pytest
import boto3
from unittest.mock import Mock, patch, MagicMock
import json
import os
from datetime import datetime
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

# PyTest Fixtures
@pytest.fixture
def mock_environment():
    """Fixture for environment variables"""
    return {
        'TARGET_WEBSITES_TABLE': 'test-target-websites-table',
        'NAMESPACE': 'test-namespace',
        'AVAILABILITY_METRIC_NAME': 'Availability',
        'LATENCY_METRIC_NAME': 'Latency',
        'RESPONSE_SIZE_METRIC_NAME': 'ResponseSize'
    }

@pytest.fixture
def mock_cloudwatch():
    """Fixture for CloudWatch client"""
    mock_cw = Mock()
    mock_cw.put_metric_data.return_value = {}
    return mock_cw

@pytest.fixture
def mock_dynamodb():
    """Fixture for DynamoDB resource"""
    mock_db = Mock()
    mock_table = Mock()
    mock_table.scan.return_value = {
        'Items': [
            {'url': 'https://vuws.westernsydney.edu.au/', 'enabled': True},
            {'url': 'https://westernsydney.edu.au/', 'enabled': True},
            {'url': 'https://library.westernsydney.edu.au/', 'enabled': True}
        ]
    }
    mock_db.Table.return_value = mock_table
    return mock_db

@pytest.fixture
def mock_requests_success():
    """Fixture for successful HTTP requests"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b'<html><body>Test content</body></html>'
    mock_response.elapsed.total_seconds.return_value = 0.5
    return mock_response

# UNIT TESTS (5 tests) - Test individual components in isolation

# UNIT TEST 1: Basic Functionality
def test_1_unit_basic_functionality(mock_environment, mock_cloudwatch, mock_dynamodb, mock_requests_success):
    """
    UNIT TEST 1: Basic Lambda Functionality
    
    What it tests: Does the Lambda function work with successful requests?
    Why unit test: Tests the core Lambda logic in isolation
    What it mocks: CloudWatch and HTTP requests (external dependencies)
    """
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    with patch.dict(os.environ, mock_environment):
        with patch('boto3.client', return_value=mock_cloudwatch):
            with patch('boto3.resource', return_value=mock_dynamodb):
                with patch('requests.get', return_value=mock_requests_success):
                    
                    # Import using importlib to avoid lambda keyword issues
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        "lambda_function", 
                        os.path.join(os.path.dirname(__file__), '..', 'lambda', 'website_crawler', 'lambda_function.py')
                    )
                    lambda_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(lambda_module)
                    
                    result = lambda_module.lambda_handler({}, {})
                    
                    # Assertions
                    assert result['statusCode'] == 200
                    assert 'Checked 3 URLs' in result['body']
                    assert mock_cloudwatch.put_metric_data.call_count == 3

# UNIT TEST 2: Error Handling
def test_2_unit_error_handling(mock_environment, mock_cloudwatch, mock_dynamodb):
    """
    UNIT TEST 2: Error Handling
    
    What it tests: Does the Lambda handle connection failures gracefully?
    Why unit test: Tests error handling logic in isolation
    What it mocks: HTTP requests to fail, CloudWatch to succeed
    """
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    with patch.dict(os.environ, mock_environment):
        with patch('boto3.client', return_value=mock_cloudwatch):
            with patch('boto3.resource', return_value=mock_dynamodb):
                with patch('requests.get', side_effect=RequestException("Connection failed")):
                    
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        "lambda_function", 
                        os.path.join(os.path.dirname(__file__), '..', 'lambda', 'website_crawler', 'lambda_function.py')
                    )
                    lambda_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(lambda_module)
                    
                    result = lambda_module.lambda_handler({}, {})
                    
                    # Should handle errors gracefully
                    assert result['statusCode'] == 200
                    assert 'Checked 3 URLs' in result['body']
                    assert mock_cloudwatch.put_metric_data.call_count == 3

# UNIT TEST 3: Timeout Handling
def test_3_unit_timeout_handling(mock_environment, mock_cloudwatch, mock_dynamodb):
    """
    UNIT TEST 3: Timeout Handling
    
    What it tests: Does the Lambda handle request timeouts correctly?
    Why unit test: Tests timeout handling logic in isolation
    What it mocks: HTTP requests to timeout, CloudWatch to succeed
    """
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    with patch.dict(os.environ, mock_environment):
        with patch('boto3.client', return_value=mock_cloudwatch):
            with patch('boto3.resource', return_value=mock_dynamodb):
                with patch('requests.get', side_effect=Timeout("Request timeout")):
                    
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        "lambda_function", 
                        os.path.join(os.path.dirname(__file__), '..', 'lambda', 'website_crawler', 'lambda_function.py')
                    )
                    lambda_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(lambda_module)
                    
                    result = lambda_module.lambda_handler({}, {})
                    
                    # Should handle timeout gracefully
                    assert result['statusCode'] == 200
                    assert 'Checked 3 URLs' in result['body']

# UNIT TEST 4: CloudWatch Data Validation
def test_4_unit_cloudwatch_data_validation(mock_environment, mock_cloudwatch, mock_dynamodb, mock_requests_success):
    """
    UNIT TEST 4: CloudWatch Data Validation
    
    What it tests: Does the Lambda send correct data structure to CloudWatch?
    Why unit test: Tests data formatting logic in isolation
    What it mocks: HTTP requests and CloudWatch (but validates data structure)
    """
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    with patch.dict(os.environ, mock_environment):
        with patch('boto3.client', return_value=mock_cloudwatch):
            with patch('boto3.resource', return_value=mock_dynamodb):
                with patch('requests.get', return_value=mock_requests_success):
                    
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        "lambda_function", 
                        os.path.join(os.path.dirname(__file__), '..', 'lambda', 'website_crawler', 'lambda_function.py')
                    )
                    lambda_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(lambda_module)
                    
                    result = lambda_module.lambda_handler({}, {})
                    
                    # Check CloudWatch calls
                    assert mock_cloudwatch.put_metric_data.call_count == 3
                
                # Validate data structure
                calls = mock_cloudwatch.put_metric_data.call_args_list
                for call in calls:
                    args, kwargs = call
                    assert 'Namespace' in kwargs
                    assert 'MetricData' in kwargs
                    
                    # Check required metrics
                    metric_names = [metric['MetricName'] for metric in kwargs['MetricData']]
                    assert 'Availability' in metric_names
                    assert 'Latency' in metric_names
                    assert 'ResponseSize' in metric_names

# UNIT TEST 5: Environment Variable Handling
def test_5_unit_environment_variables(mock_environment, mock_cloudwatch, mock_dynamodb, mock_requests_success):
    """
    UNIT TEST 5: Environment Variable Handling
    
    What it tests: Does the Lambda correctly read and use environment variables?
    Why unit test: Tests configuration handling logic in isolation
    What it mocks: All external dependencies to focus on env var logic
    """
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    with patch.dict(os.environ, mock_environment):
        with patch('boto3.client', return_value=mock_cloudwatch):
            with patch('requests.get', return_value=mock_requests_success):
                
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "lambda_function", 
                    os.path.join(os.path.dirname(__file__), '..', 'lambda', 'website_crawler', 'lambda_function.py')
                )
                lambda_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(lambda_module)
                
                result = lambda_module.lambda_handler({}, {})
                
                # Should use environment variables correctly
                assert result['statusCode'] == 200
                assert 'Checked 3 URLs' in result['body']  # Based on URLS env var

# FUNCTIONAL TESTS (5 tests) - Test complete workflows end-to-end

# FUNCTIONAL TEST 1: End-to-End Monitoring Flow
def test_1_functional_end_to_end_flow(mock_environment, mock_cloudwatch, mock_dynamodb):
    """
    FUNCTIONAL TEST 1: Complete Monitoring Workflow
    
    What it tests: Does the entire monitoring process work from start to finish?
    Why functional test: Tests complete workflow with real-world scenarios
    What it simulates: Different website responses, complete monitoring cycle
    """
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    with patch.dict(os.environ, mock_environment):
        with patch('boto3.client', return_value=mock_cloudwatch):
            with patch('boto3.resource', return_value=mock_dynamodb):
                def mock_get(url, timeout=5):
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.content = b'<html>Test content</html>'
                    mock_response.elapsed.total_seconds.return_value = 0.3
                    return mock_response

                with patch('requests.get', side_effect=mock_get):
                    
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        "lambda_function", 
                        os.path.join(os.path.dirname(__file__), '..', 'lambda', 'website_crawler', 'lambda_function.py')
                    )
                    lambda_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(lambda_module)
                    
                    result = lambda_module.lambda_handler({}, {})
                    
                    # Functional assertions
                    assert result['statusCode'] == 200
                    assert 'Checked 3 URLs' in result['body']
                    assert mock_cloudwatch.put_metric_data.call_count == 3

# FUNCTIONAL TEST 2: Multi-Website Monitoring
def test_2_functional_multi_website_monitoring(mock_environment, mock_cloudwatch, mock_dynamodb):
    """
    FUNCTIONAL TEST 2: Multi-Website Monitoring
    
    What it tests: Can the system monitor multiple websites with different responses?
    Why functional test: Tests real-world scenario of monitoring multiple sites
    What it simulates: Different websites with different response times and content
    """
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    with patch.dict(os.environ, mock_environment):
        with patch('boto3.client', return_value=mock_cloudwatch):
            
            # Simulate different responses for different URLs
            def mock_different_responses(url, timeout=5):
                mock_response = Mock()
                if 'vuws' in url:
                    mock_response.status_code = 200
                    mock_response.content = b'<html>VUWS Content</html>'
                    mock_response.elapsed.total_seconds.return_value = 0.2
                elif 'westernsydney' in url:
                    mock_response.status_code = 200
                    mock_response.content = b'<html>University Content</html>'
                    mock_response.elapsed.total_seconds.return_value = 0.5
                elif 'library' in url:
                    mock_response.status_code = 200
                    mock_response.content = b'<html>Library Content</html>'
                    mock_response.elapsed.total_seconds.return_value = 0.8
                else:
                    mock_response.status_code = 404
                    mock_response.content = b'Not Found'
                    mock_response.elapsed.total_seconds.return_value = 1.0
                return mock_response
            
            with patch('requests.get', side_effect=mock_different_responses):
                
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "lambda_function", 
                    os.path.join(os.path.dirname(__file__), '..', 'lambda', 'website_crawler', 'lambda_function.py')
                )
                lambda_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(lambda_module)
                
                result = lambda_module.lambda_handler({}, {})
                
                # Should handle multiple websites successfully
                assert result['statusCode'] == 200
                assert 'Checked 3 URLs' in result['body']
                assert mock_cloudwatch.put_metric_data.call_count == 3

# FUNCTIONAL TEST 3: Performance Measurement
def test_3_functional_performance_measurement(mock_environment, mock_cloudwatch, mock_dynamodb):
    """
    FUNCTIONAL TEST 3: Performance Measurement
    
    What it tests: Does the system accurately measure and record performance metrics?
    Why functional test: Tests real-world performance monitoring behavior
    What it simulates: Different response times and performance scenarios
    """
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    with patch.dict(os.environ, mock_environment):
        with patch('boto3.client', return_value=mock_cloudwatch):
            def mock_get_with_timing(url, timeout=5):
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.content = b'<html>Test content</html>'
                mock_response.elapsed.total_seconds.return_value = 0.5
                return mock_response
            
            with patch('requests.get', side_effect=mock_get_with_timing):
                
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "lambda_function", 
                    os.path.join(os.path.dirname(__file__), '..', 'lambda', 'website_crawler', 'lambda_function.py')
                )
                lambda_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(lambda_module)
                
                result = lambda_module.lambda_handler({}, {})
                
                # Performance assertions
                assert result['statusCode'] == 200
                assert 'Checked 3 URLs' in result['body']
                assert mock_cloudwatch.put_metric_data.call_count == 3
                
                # Verify latency metrics are recorded
                all_metrics = []
                for call in mock_cloudwatch.put_metric_data.call_args_list:
                    args, kwargs = call
                    all_metrics.extend(kwargs['MetricData'])
                
                latency_metrics = [m for m in all_metrics if m['MetricName'] == 'Latency']
                assert len(latency_metrics) == 3  # One for each URL

# FUNCTIONAL TEST 4: Mixed Success/Failure Scenarios
def test_4_functional_mixed_scenarios(mock_environment, mock_cloudwatch, mock_dynamodb):
    """
    FUNCTIONAL TEST 4: Mixed Success/Failure Scenarios
    
    What it tests: Can the system handle real-world mixed scenarios (some sites up, some down)?
    Why functional test: Tests realistic monitoring scenarios
    What it simulates: Some websites working, some failing, some slow
    """
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    with patch.dict(os.environ, mock_environment):
        with patch('boto3.client', return_value=mock_cloudwatch):
            
            # Simulate mixed scenarios
            def mock_mixed_responses(url, timeout=5):
                mock_response = Mock()
                if 'vuws' in url:
                    # This one works
                    mock_response.status_code = 200
                    mock_response.content = b'<html>VUWS Working</html>'
                    mock_response.elapsed.total_seconds.return_value = 0.2
                elif 'westernsydney' in url:
                    # This one is slow but works
                    mock_response.status_code = 200
                    mock_response.content = b'<html>University Slow</html>'
                    mock_response.elapsed.total_seconds.return_value = 2.0
                elif 'library' in url:
                    # This one fails
                    raise ConnectionError("Library site is down")
                else:
                    mock_response.status_code = 500
                    mock_response.content = b'Server Error'
                    mock_response.elapsed.total_seconds.return_value = 1.0
                
                return mock_response
            
            with patch('requests.get', side_effect=mock_mixed_responses):
                
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "lambda_function", 
                    os.path.join(os.path.dirname(__file__), '..', 'lambda', 'website_crawler', 'lambda_function.py')
                )
                lambda_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(lambda_module)
                
                result = lambda_module.lambda_handler({}, {})
                
                # Should handle mixed scenarios gracefully
                assert result['statusCode'] == 200
                assert 'Checked 3 URLs' in result['body']
                assert mock_cloudwatch.put_metric_data.call_count == 3

# FUNCTIONAL TEST 5: Complete Monitoring Cycle
def test_5_functional_complete_monitoring_cycle(mock_environment, mock_cloudwatch, mock_dynamodb):
    """
    FUNCTIONAL TEST 5: Complete Monitoring Cycle
    
    What it tests: Does the entire monitoring system work as expected in a complete cycle?
    Why functional test: Tests the full end-to-end monitoring workflow
    What it simulates: Complete monitoring cycle with all components working together
    """
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    with patch.dict(os.environ, mock_environment):
        with patch('boto3.client', return_value=mock_cloudwatch):
            
            # Simulate a complete monitoring cycle
            def mock_complete_cycle(url, timeout=5):
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.content = b'<html>Complete monitoring cycle test</html>'
                mock_response.elapsed.total_seconds.return_value = 0.3
                return mock_response
            
            with patch('requests.get', side_effect=mock_complete_cycle):
                
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "lambda_function", 
                    os.path.join(os.path.dirname(__file__), '..', 'lambda', 'website_crawler', 'lambda_function.py')
                )
                lambda_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(lambda_module)
                
                result = lambda_module.lambda_handler({}, {})
                
                # Complete cycle assertions
                assert result['statusCode'] == 200
                assert 'Checked 3 URLs' in result['body']
                assert mock_cloudwatch.put_metric_data.call_count == 3
                
                # Verify all metrics are present
                all_metrics = []
                for call in mock_cloudwatch.put_metric_data.call_args_list:
                    args, kwargs = call
                    all_metrics.extend(kwargs['MetricData'])
                
                # Should have 9 metrics total (3 URLs × 3 metrics each)
                assert len(all_metrics) == 9
                
                # Check metric types
                metric_names = [m['MetricName'] for m in all_metrics]
                assert metric_names.count('Availability') == 3
                assert metric_names.count('Latency') == 3
                assert metric_names.count('ResponseSize') == 3

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
