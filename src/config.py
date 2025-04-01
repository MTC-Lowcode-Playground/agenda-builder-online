import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates')
    STATIC_PATH = os.path.join(BASE_DIR, 'static')
    LOGO_PATH = os.path.join(BASE_DIR, 'logos')
    DOCX_TEMPLATE = os.path.join(TEMPLATE_PATH, 'DATE-CUST-TOPICAgenda.docx')
    JSON_DATA_FILE = os.path.join(BASE_DIR, 'agenda_data.json')
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'generated_docs')
    
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)