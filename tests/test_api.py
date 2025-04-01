import json
import unittest
from app import app

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_generate_agenda(self):
        json_data = {
            "customer": "Test Customer",
            "date": "2023-10-01",
            "summary": "Test Summary",
            "title": "Test Title",
            "logo": "test_logo.png",
            "primaries": [
                {"name": "Primary One", "role": "Role One"},
                {"name": "Primary Two", "role": "Role Two"}
            ],
            "supporting": [
                {"name": "Supporting One", "role": "Role One"}
            ],
            "agenda_items": [
                {"time": "10:00 AM", "owner": "Owner One", "topic": "Topic One", "description": "Description One"},
                {"time": "11:00 AM", "owner": "Owner Two", "topic": "Topic Two", "description": "Description Two"}
            ]
        }
        response = self.app.post('/generate', json=json_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('download_link', json.loads(response.data))

    def test_invalid_json(self):
        response = self.app.post('/generate', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', json.loads(response.data))

if __name__ == '__main__':
    unittest.main()