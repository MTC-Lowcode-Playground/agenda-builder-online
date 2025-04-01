from docxtpl import DocxTemplate
import json
import os
import uuid
from datetime import datetime

def create_agenda_doc(data, template_path, output_path=None, logo_path=None):
    """
    Core function to create an agenda document from JSON data
    
    Args:
        data: Dictionary or JSON string of agenda data
        template_path: Path to the template DOCX file
        output_path: Path to save the output (generated if None)
        logo_path: Optional path to a logo file to include
    
    Returns:
        Path to the generated document
    """
    # Parse JSON if string was provided
    if isinstance(data, str):
        data = json.loads(data)
    
    # Load the template
    doc = DocxTemplate(template_path)
    
    # Add logo if provided
    if logo_path:
        data['has_logo'] = True
        data['logo_path'] = logo_path
    else:
        data['has_logo'] = False
    
    # Render the document
    doc.render(data)
    
    # Generate output path if not provided
    if not output_path:
        os.makedirs('output', exist_ok=True)
        current_date = datetime.now().strftime("%Y%m%d")
        customer = data.get('customer', 'Customer')
        topic = data.get('topic', 'Meeting')
        filename = f"{current_date}-{customer}-{topic}Agenda-{uuid.uuid4()}.docx"
        output_path = os.path.join('output', filename)
    
    # Save the document
    doc.save(output_path)
    
    return output_path