import json
import os
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from docx import Document
from docx.shared import Inches

def create_agenda_doc(json_data, template_path, output_path):
    """
    Generates an agenda document from the provided JSON data using a DOCX template.
    
    Expected JSON schema:
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "customer": {
                "type": "string"
            },
            "date": {
                "type": "string",
                "format": "date"
            },
            "summary": {
                "type": "string"
            },
            "title": {
                "type": "string"
            },
            "logo": {
                "type": "string"
            },
            "primaries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": { "type": "string" },
                        "role": { "type": "string" }
                    },
                    "required": ["name", "role"]
                }
            },
            "supporting": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": { "type": "string" },
                        "role": { "type": "string" }
                    },
                    "required": ["name", "role"]
                }
            },
            "agenda_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "time": { "type": "string" },
                        "owner": { "type": "string" },
                        "topic": { "type": "string" },
                        "description": { "type": "string" }
                    },
                    "required": ["time", "owner", "topic", "description"]
                }
            }
        },
        "required": ["customer", "date", "summary", "title", "primaries", "supporting", "agenda_items"]
    }
    """
    # Load the DOCX template
    doc = DocxTemplate(template_path)
    
    # Prepare context from the JSON data, including the new "title", "primaries", and "supporting" fields.
    context = {
        "customer": json_data.get("customer", ""),
        "date": json_data.get("date", ""),
        "title": json_data.get("title", ""),
        "summary": json_data.get("summary", ""),
        "primaries": json_data.get("primaries", []),
        "supporting": json_data.get("supporting", []),
        "agenda_items": json_data.get("agenda_items", [])
    }
    
    # If a logo image path is provided and the file exists, prepare an InlineImage.
    logo_path = json_data.get("logo", "")
    if logo_path and os.path.exists(logo_path):
        context["logo"] = InlineImage(doc, logo_path, width=Mm(50))
    else:
        context["logo"] = ""  # or set a default placeholder if desired

    # Render the template with the context
    doc.render(context)
    
    # Save the generated document
    doc.save(output_path)
    print(f"Agenda document generated successfully at: {output_path}")

def post_process_document(docx_path):
    """
    Post-processes the generated DOCX file to:
    1. Remove the first column from agenda items table
    2. Adjust column widths for better appearance
    """
    # Open the document
    doc = Document(docx_path)
    
    # Find the agenda items table (assuming it's the largest table or has specific content)
    agenda_table = None
    for table in doc.tables:
        # You may need to customize this logic to reliably identify your agenda table
        if len(table.rows) > 1:  # More than just header row
            agenda_table = table
            break
    
    if agenda_table:
        # Remove the first column (this requires XML manipulation)
        for row in agenda_table.rows:
            # Get the XML element for the row
            xml_row = row._tr
            # Remove the first cell if it exists
            if xml_row.tc_lst:
                xml_row.remove(xml_row.tc_lst[0])
        
        # Adjust the remaining columns to appropriate widths
        # Assuming we now have 3 columns (time, owner, topic/description)
        if len(agenda_table.columns) >= 3:
            agenda_table.columns[0].width = Inches(0.8)   # Time column
            agenda_table.columns[1].width = Inches(1.2)   # Owner column
            agenda_table.columns[2].width = Inches(4.0)   # Topic/Description column
    
    # Save the modified document
    doc.save(docx_path)
    print(f"Document post-processed successfully: {docx_path}")

if __name__ == "__main__":
    # Example: Load JSON from a file provided by your external system
    json_file_path = "agenda_data.json"
    
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            agenda_data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        exit(1)
    
    # Define the path to your DOCX template
    template_path = "DATE-CUST-TOPICAgenda.docx"
    
    # Compute the output path based on the provided agenda data.
    # This replaces spaces with underscores to form a valid file name.
    date = agenda_data.get("date", "DATE").replace(" ", "_")
    customer = agenda_data.get("customer", "CUST").replace(" ", "_")
    title = agenda_data.get("title", "TOPIC").replace(" ", "_")
    output_path = f"{date}-{customer}-{title}Agenda.docx"
    
    # Generate the document from template
    create_agenda_doc(agenda_data, template_path, output_path)
    
    # Post-process the document to fix table formatting
    post_process_document(output_path)
