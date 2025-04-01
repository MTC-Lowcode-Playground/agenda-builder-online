def save_json_to_file(json_data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

def load_json_from_file(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_document_link(output_path):
    return f"/download/{os.path.basename(output_path)}"

def clean_up_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)