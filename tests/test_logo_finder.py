import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add the src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app import app

class LogoFinderTests(unittest.TestCase):
    
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_find_logo_no_company_name(self):
        """Test that an error is returned when no company name is provided"""
        response = self.client.get('/find-logo')
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Company name is required')
    
    def test_find_logo_mock_data_known_company(self):
        """Test that known companies in mock data return the expected logo"""
        # This assumes 'microsoft' is in your MOCK_LOGO_RESULTS
        response = self.client.get('/find-logo?company=microsoft')
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('logoUrl', data)
    
    def test_find_logo_mock_data_unknown_company(self):
        """Test that unknown companies return the default mock logo"""
        response = self.client.get('/find-logo?company=nonexistentcompany123')
        data = json.loads(response.data)
        self.assertTrue(data['success'])  # Default should still be successful
        self.assertIn('logoUrl', data)
    
    @patch('app.USE_MOCK_DATA', False)
    @patch('app.requests.get')
    def test_find_logo_bing_api_success(self, mock_get):
        """Test the Bing API path with a mocked successful response"""
        # Mock a successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'value': [
                {
                    'contentUrl': 'https://example.com/logo.png',
                    'thumbnailUrl': 'https://example.com/logo-thumb.png',
                    'encodingFormat': 'png'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        response = self.client.get('/find-logo?company=microsoft')
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['logoUrl'], 'https://example.com/logo.png')
    
    @patch('app.USE_MOCK_DATA', False)
    @patch('app.requests.get')
    def test_find_logo_bing_api_failure(self, mock_get):
        """Test the Bing API path with a mocked failed response"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        response = self.client.get('/find-logo?company=microsoft')
        data = json.loads(response.data)
        
        self.assertFalse(data['success'])
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()