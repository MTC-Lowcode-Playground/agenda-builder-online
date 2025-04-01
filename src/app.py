import logging
logging.basicConfig(level=logging.DEBUG)

from flask import Flask, render_template, request, send_file, jsonify
from config import USE_AZURE_STORAGE, AZURE_STORAGE_CONNECTION_STRING, AZURE_CONTAINER_NAME
import json
import os
from agenda_builder.core import create_agenda_doc
from datetime import datetime

try:
    from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
except ImportError:
    pass

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

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

    template_locations = [
        os.path.join('templates', 'DATE-CUST-TOPICAgenda.docx'),
        os.path.join('src', 'templates', 'DATE-CUST-TOPICAgenda.docx'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'templates', 'DATE-CUST-TOPICAgenda.docx'),
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
        
    try:
        output_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'output', 
            f"agenda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        logo_path = None
        logo_temp = None
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file.filename:
                content_type = logo_file.content_type
                if not content_type or not content_type.startswith('image/'):
                    app.logger.warning(f"File doesn't appear to be an image: {content_type}")
                else:
                    temp_logo_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_logos')
                    os.makedirs(temp_logo_dir, exist_ok=True)
                    
                    logo_temp_path = os.path.join(temp_logo_dir, f"logo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                    logo_file.save(logo_temp_path)
                    app.logger.info(f"Saved uploaded logo to: {logo_temp_path}")
                    
                    if os.path.exists(logo_temp_path) and os.path.getsize(logo_temp_path) > 0:
                        logo_path = logo_temp_path
                        app.logger.info(f"Logo file verified: {logo_path} (size: {os.path.getsize(logo_path)} bytes)")
                    else:
                        app.logger.error(f"Logo file not created properly: {logo_temp_path}")
        
        app.logger.info(f"Calling create_agenda_doc with logo_path: {logo_path}")
        
        try:
            create_agenda_doc(agenda_data, template_path, output_path, logo_path)
        except Exception as e:
            app.logger.warning(f"Document generation with logo failed: {str(e)}")
            app.logger.info("Trying again without logo")
            create_agenda_doc(agenda_data, template_path, output_path, None)
        
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            app.logger.error(f"Output file not created properly at: {output_path}")
            return "Error generating document", 500
            
        app.logger.info(f"Document generated successfully at: {output_path}")
        
        app.logger.debug(f"About to send file: {output_path}, exists={os.path.exists(output_path)}, size={os.path.getsize(output_path)}")
        
        if USE_AZURE_STORAGE:
            app.logger.info("Azure Storage enabled. Uploading file to Blob Storage.")
            connection_string = AZURE_STORAGE_CONNECTION_STRING
            container_name = AZURE_CONTAINER_NAME
            if not connection_string:
                app.logger.error("Azure connection string not found.")
                return "Azure storage connection string not found", 500
            
            try:
                blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                container_client = blob_service_client.get_container_client(container_name)
                container_client.create_container(exist_ok=True)
                
                blob_name = os.path.basename(output_path)
                with open(output_path, "rb") as data:
                    container_client.upload_blob(blob_name, data, overwrite=True)
                
                sas_token = generate_blob_sas(
                    account_name=blob_service_client.account_name,
                    container_name=container_name,
                    blob_name=blob_name,
                    account_key=blob_service_client.credential.account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow().replace(hour=23, minute=59, second=59)
                )
                blob_url = f"{container_client.url}/{blob_name}?{sas_token}"
                app.logger.info(f"Document uploaded to: {blob_url}")
                
                return jsonify({"downloadUrl": blob_url})
            except Exception as e:
                app.logger.error(f"Error uploading file to Azure: {str(e)}")
                return f"Error uploading file to Azure: {str(e)}", 500
        else:
            try:
                customer = agenda_data.get('customer', 'Customer')
                date_str = agenda_data.get('date', 'DATE')
                customer = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in customer)
                date_str = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in date_str)
                filename = f"{date_str}-{customer}Agenda.docx"
                
                app.logger.info(f"Sending file with name: {filename}")
                
                response = send_file(
                    output_path,
                    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    as_attachment=True
                )
                
                response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
                
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