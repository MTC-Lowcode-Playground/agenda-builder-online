import logging
logging.basicConfig(level=logging.DEBUG)

from flask import Flask, render_template, request, send_file, jsonify
import json
import os
from agenda_builder.core import create_agenda_doc
from datetime import datetime

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# Configuration - store in environment variables or Azure Key Vault
USE_AZURE_STORAGE = os.environ.get("USE_AZURE_STORAGE", "False").lower() == "true"

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
        # Create output path without immediately creating the file
        output_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'output', 
            f"agenda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Handle uploaded logo file with more verification
        logo_path = None
        logo_temp = None
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file.filename:
                # Verify the file is actually an image
                content_type = logo_file.content_type
                if not content_type or not content_type.startswith('image/'):
                    app.logger.warning(f"File doesn't appear to be an image: {content_type}")
                else:
                    # Make a dedicated directory for temporary logos
                    temp_logo_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_logos')
                    os.makedirs(temp_logo_dir, exist_ok=True)
                    
                    # Use a non-deleted temporary file with a stable name
                    logo_temp_path = os.path.join(temp_logo_dir, f"logo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                    logo_file.save(logo_temp_path)
                    app.logger.info(f"Saved uploaded logo to: {logo_temp_path}")
                    
                    # Verify the file was actually created and has content
                    if os.path.exists(logo_temp_path) and os.path.getsize(logo_temp_path) > 0:
                        logo_path = logo_temp_path
                        app.logger.info(f"Logo file verified: {logo_path} (size: {os.path.getsize(logo_path)} bytes)")
                    else:
                        app.logger.error(f"Logo file not created properly: {logo_temp_path}")
        
        # Generate the document with logo if available
        app.logger.info(f"Calling create_agenda_doc with logo_path: {logo_path}")
        
        # Try with logo first, but have a fallback without logo
        try:
            create_agenda_doc(agenda_data, template_path, output_path, logo_path)
        except Exception as e:
            app.logger.warning(f"Document generation with logo failed: {str(e)}")
            app.logger.info("Trying again without logo")
            
            # Try again without the logo
            create_agenda_doc(agenda_data, template_path, output_path, None)
        
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
        app.logger.exception("Full exception details:")
        return f"Error generating document: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)