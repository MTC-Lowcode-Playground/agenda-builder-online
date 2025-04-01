# Agenda Builder Online

## Overview
Agenda Builder Online is a web application that allows users to generate agenda documents from JSON input. The application utilizes a DOCX template to create formatted agenda documents, which can be downloaded or accessed via a link.

## Features
- JSON input field for user data
- Generate button to create the agenda document
- Automatic download or link to the generated document
- Responsive design with CSS styling
- JavaScript handling for user interactions

## Project Structure
```
agenda-builder-online
├── src
│   ├── static
│   │   ├── css
│   │   │   └── styles.css
│   │   └── js
│   │       └── main.js
│   ├── templates
│   │   ├── base.html
│   │   └── index.html
│   ├── app.py
│   ├── agenda_builder
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   └── utils.py
│   └── config.py
├── templates
│   └── DATE-CUST-TOPICAgenda.docx
├── logos
│   └── README.md
├── tests
│   ├── __init__.py
│   ├── test_generator.py
│   └── test_api.py
├── .github
│   └── workflows
│       └── azure-deploy.yml
├── requirements.txt
├── .gitignore
├── README.md
└── azure.yaml
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd agenda-builder-online
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```
   python src/app.py
   ```
2. Open your web browser and go to `http://localhost:5000`.
3. Enter your JSON data in the input field and click the "Generate" button to create your agenda document.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.