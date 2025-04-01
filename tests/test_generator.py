import unittest
import json
import tempfile
import os
from agenda_builder.generator import create_agenda_doc
from unittest.mock import patch, MagicMock

class TestGenerator(unittest.TestCase):

    @patch('agenda_builder.generator.DocxTemplate')
    @patch('agenda_builder.generator.InlineImage')
    def test_create_agenda_doc(self, mock_inline_image, mock_docx_template):
        mock_doc = MagicMock()
        mock_docx_template.return_value = mock_doc
        
        json_data = {
            "customer": "Test Customer",
            "date": "2023-10-01",
            "summary": "Test Summary",
            "title": "Test Title",
            "logo": "test_logo.png",
            "primaries": [{"name": "Primary 1", "role": "Role 1"}],
            "supporting": [{"name": "Supporting 1", "role": "Role 2"}],
            "agenda_items": [
                {"time": "10:00 AM", "owner": "Owner 1", "topic": "Topic 1", "description": "Description 1"},
                {"time": "11:00 AM", "owner": "Owner 2", "topic": "Topic 2", "description": "Description 2"}
            ]
        }
        
        template_path = "path/to/template.docx"
        output_path = "path/to/output.docx"
        
        create_agenda_doc(json_data, template_path, output_path)
        
        mock_docx_template.assert_called_once_with(template_path)
        mock_doc.render.assert_called_once()
        mock_doc.save.assert_called_once_with(output_path)

    @patch('app.create_agenda_doc')
    def test_generate_with_logo_url(self, mock_create_agenda):
        """Test document generation with a logo URL"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
        mock_create_agenda.return_value = temp_file.name
        
        # JSON data with logo URL
        json_with_logo = json.dumps({
            "title": "Test Meeting",
            "customer": "Test Corp",
            "date": "2025-04-01",
            "logo_url": "https://example.com/logo.png",
            "agenda_items": [
                {"time": "10:00", "topic": "Introduction", "owner": "Person 1"}
            ]
        })
        
        response = self.client.post('/generate', 
                                  data={'json_data': json_with_logo, 'logoSource': 'suggested', 'logoUrl': 'https://example.com/logo.png'},
                                  content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        # Check that create_agenda_doc was called with the logo URL
        args, kwargs = mock_create_agenda.call_args
        self.assertIsNotNone(args[1])  # Logo path should be passed
        
        # Clean up temp file
        os.unlink(temp_file.name)

    @patch('app.create_agenda_doc')
    def test_generate_with_uploaded_logo(self, mock_create_agenda):
        """Test document generation with an uploaded logo file"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
        mock_create_agenda.return_value = temp_file.name
        
        # Create a test logo file
        test_logo = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        test_logo.write(b'fake image data')
        test_logo.close()
        
        with open(test_logo.name, 'rb') as logo_file:
            response = self.client.post('/generate', 
                                    data={
                                        'json_data': self.valid_json, 
                                        'logoSource': 'uploaded',
                                        'logo': (logo_file, 'test_logo.png')
                                    },
                                    content_type='multipart/form-data')
        
            self.assertEqual(response.status_code, 200)
            # Check that create_agenda_doc was called with a logo path
            args, kwargs = mock_create_agenda.call_args
            self.assertIsNotNone(args[1])  # Logo path should be passed
        
        # Clean up temp files
        os.unlink(temp_file.name)
        os.unlink(test_logo.name)

if __name__ == '__main__':
    unittest.main()