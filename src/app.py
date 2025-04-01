import logging
logging.basicConfig(level=logging.DEBUG)

from flask import Flask, render_template, request, send_file, jsonify
import json
import os
import requests
from agenda_builder.core import create_agenda_doc
from tempfile import NamedTemporaryFile
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from datetime import datetime

# Import mock data for local testing
from mock_data import MOCK_LOGO_RESULTS, DEFAULT_MOCK_LOGO

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# Configuration - store in environment variables or Azure Key Vault
BING_SEARCH_ENDPOINT = os.environ.get("BING_SEARCH_ENDPOINT", "https://api.bing.microsoft.com/v7.0/images/search")
BING_SUBSCRIPTION_KEY = os.environ.get("BING_SUBSCRIPTION_KEY", "your-bing-api-key")
USE_AZURE_STORAGE = os.environ.get("USE_AZURE_STORAGE", "False").lower() == "true"

# Determine if we're in local development mode
USE_MOCK_DATA = os.environ.get("USE_MOCK_DATA", "True").lower() == "true"

# Optional: Use Azure Key Vault to retrieve the API key securely
def get_bing_api_key():
    try:
        keyvault_name = os.environ.get("KEYVAULT_NAME")
        if keyvault_name:
            credential = DefaultAzureCredential()
            keyvault_url = f"https://{keyvault_name}.vault.azure.net/"
            client = SecretClient(vault_url=keyvault_url, credential=credential)
            return client.get_secret("BING-SEARCH-KEY").value
        return BING_SUBSCRIPTION_KEY
    except Exception:
        return BING_SUBSCRIPTION_KEY

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    json_data = request.form.get('json_data')
    if not json_data:
        app.logger.error(f"Missing JSON data. Form data: {request.form}")
        return "Invalid JSON data", 400

    try:
        agenda_data = json.loads(json_data)
    except json.JSONDecodeError as e:
        app.logger.error(f"JSON decode error: {str(e)}")
        return "Error decoding JSON", 400

    # Try multiple possible template locations
    template_locations = [
        # Relative to current working directory (project root)
        os.path.join('templates', 'DATE-CUST-TOPICAgenda.docx'),
        
        # Inside src directory
        os.path.join('src', 'templates', 'DATE-CUST-TOPICAgenda.docx'),
        
        # One directory up from src
        os.path.join(os.path.dirname(__file__), '..', '..', 'templates', 'DATE-CUST-TOPICAgenda.docx'),
        
        # Inside assets directory if it exists
        os.path.join('assets', 'templates', 'DATE-CUST-TOPICAgenda.docx')
    ]
    
    template_path = None
    for location in template_locations:
        if os.path.exists(location):
            template_path = location
            app.logger.info(f"Found template at: {template_path}")
            break
    
    if not template_path:
        app.logger.error(f"Template file not found. Tried: {template_locations}")
        return "Template file not found. Make sure you have a template file named 'DATE-CUST-TOPICAgenda.docx' in the templates directory.", 500
        
    # Create the document
    try:
        with NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            output_path = temp_file.name
        
        # Handle logo from the form
        logo_path = None
        logo_source = request.form.get('logoSource')
        
        app.logger.info(f"Logo source: {logo_source}")
        
        if logo_source == 'suggested':
            # Use the suggested logo URL
            logo_url = request.form.get('logoUrl')
            app.logger.info(f"Using suggested logo URL: {logo_url}")
            logo_path = logo_url
            
        elif logo_source == 'uploaded':
            # Handle uploaded logo file
            if 'logo' in request.files:
                logo_file = request.files['logo']
                if logo_file.filename:
                    # Save the uploaded file to a temporary location
                    with NamedTemporaryFile(delete=False, suffix='.png') as logo_temp:
                        logo_temp_path = logo_temp.name
                    
                    logo_file.save(logo_temp_path)
                    app.logger.info(f"Saved uploaded logo to: {logo_temp_path}")
                    logo_path = logo_temp_path
            else:
                app.logger.warning("Logo source is 'uploaded' but no file was provided")
        
        # Generate the document with logo if available
        app.logger.info(f"Calling create_agenda_doc with logo_path: {logo_path}")
        create_agenda_doc(agenda_data, template_path, output_path, logo_path)
        
        # Verify file was created
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            app.logger.error(f"Output file not created properly at: {output_path}")
            return "Error generating document", 500
            
        app.logger.info(f"Document generated successfully at: {output_path}")
        
        # Debug line before sending file
        app.logger.debug(f"About to send file: {output_path}, exists={os.path.exists(output_path)}, size={os.path.getsize(output_path)}")
        
        if USE_AZURE_STORAGE:
            # This branch would upload to Azure Blob Storage
            # Not implemented in this local version
            pass
        else:
            # Local file serving - add some extra error handling
            try:
                # Build a more descriptive filename with just customer and date
                customer = agenda_data.get('customer', 'Customer')
                
                # Just use the date from the JSON, with a simple fallback
                date_str = agenda_data.get('date', 'DATE')
                
                # Sanitize filename components
                customer = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in customer)
                date_str = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in date_str)
                
                # Create the filename - simpler structure
                filename = f"{date_str}-{customer}Agenda.docx"
                
                app.logger.info(f"Sending file with name: {filename}")
                
                # Create a response object that works with all Flask versions
                response = send_file(
                    output_path,
                    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    as_attachment=True
                )
                
                # Set the Content-Disposition header explicitly
                response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
                
                # Log the actual header for debugging
                app.logger.debug(f"Content-Disposition header: {response.headers.get('Content-Disposition')}")
                
                return response
            except Exception as e:
                app.logger.error(f"Error sending file: {str(e)}")
                return f"Error downloading document: {str(e)}", 500
        
    except Exception as e:
        app.logger.error(f"Error in document generation: {str(e)}")
        return f"Error generating document: {str(e)}", 500

@app.route('/find-logo')
def find_logo():
    company_name = request.args.get('company', '').strip().lower()
    if not company_name:
        return jsonify({'success': False, 'error': 'Company name is required'})
    
    # Use mock data if in local development mode
    if USE_MOCK_DATA:
        app.logger.info(f"Using mock data for company: {company_name}")
        
        # Find the closest match in our mock data
        for key in MOCK_LOGO_RESULTS:
            if key in company_name or company_name in key:
                return jsonify(MOCK_LOGO_RESULTS[key])
        
        # If no specific match found, return default mock logo
        return jsonify(DEFAULT_MOCK_LOGO)
    
    # Otherwise, use real Bing Search API
    try:
        # Use Bing Search API to find the company logo
        api_key = get_bing_api_key()
        search_term = f"{company_name} logo transparent"
        
        headers = {
            'Ocp-Apim-Subscription-Key': api_key,
        }
        
        params = {
            'q': search_term,
            'count': 5,  # Get a few options
            'imageType': 'Transparent',  # Prefer transparent logos
            'license': 'Public',  # Try to get publicly usable images
            'safeSearch': 'Strict'
        }
        
        response = requests.get(BING_SEARCH_ENDPOINT, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if 'value' in data and len(data['value']) > 0:
                # Find the best logo image - prefer transparent PNG/SVG files
                best_logo = None
                for image in data['value']:
                    if image.get('encodingFormat', '').lower() in ['png', 'svg']:
                        best_logo = image
                        break
                
                # If no PNG/SVG found, just use the first result
                if not best_logo and data['value']:
                    best_logo = data['value'][0]
                
                if best_logo:
                    return jsonify({
                        'success': True, 
                        'logoUrl': best_logo['contentUrl'],
                        'thumbnailUrl': best_logo.get('thumbnailUrl', best_logo['contentUrl']),
                        'additionalResults': [img['contentUrl'] for img in data['value'][:4]]
                    })
            
            return jsonify({'success': False, 'error': 'No suitable logo found'})
        else:
            return jsonify({'success': False, 'error': f'Search API error: {response.status_code}'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)