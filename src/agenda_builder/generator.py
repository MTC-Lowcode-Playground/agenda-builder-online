from flask import Flask, request, jsonify, send_file
import json
import os
from agenda_builder.core import create_agenda_doc

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    template_path = os.path.join('templates', 'DATE-CUST-TOPICAgenda.docx')
    output_path = f"{data['date'].replace(' ', '_')}-{data['customer'].replace(' ', '_')}-{data['title'].replace(' ', '_')}Agenda.docx"
    
    try:
        create_agenda_doc(data, template_path, output_path)
        return jsonify({'message': 'Document generated successfully', 'file': output_path}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)