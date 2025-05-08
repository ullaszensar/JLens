# JLens - Java J2EE Project Analyzer

JLens is a comprehensive tool for analyzing Java J2EE projects, providing visualizations, structure analysis, and UML diagrams to help you understand complex Java enterprise applications.

![JLens - Zensar Diamond Team](generated-icon.png)

## Features

- **Project Structure Analysis**: Visualize project directory hierarchy, file types, and architectural layers
- **API Endpoint Detection**: Identify REST endpoints, HTTP methods, and API relationships
- **UML Class Structure**: View class relationships, attributes, and methods in tabular format
- **Batch Process Analysis**: Detect scheduled jobs and batch processing components
- **Sequence Diagrams**: Visualize API call sequences and flow
- **Functional Flow**: Map the business logic flow across components

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Option 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/jlens.git
cd jlens

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Direct Installation

```bash
# Install dependencies directly
pip install streamlit pandas plotly javalang networkx pygraphviz
```

### Required Packages

- `streamlit`: Web application framework
- `pandas`: Data manipulation library
- `plotly`: Interactive visualization library
- `javalang`: Java source code parsing
- `networkx`: Graph creation and analysis
- `pygraphviz`: Graph visualization toolkit

## Running JLens

```bash
# Start the JLens application
streamlit run app.py
```

The application will be available at http://localhost:5000

## Usage

1. **Upload Project**: Use the file uploader to select a ZIP file containing your Java J2EE project
2. **Configure Analysis**: Select which aspects of the project to analyze
3. **View Results**: Navigate through the tabs to explore different visualizations and insights
4. **Export Data**: Use the download buttons to export data as CSV, JSON, or interactive charts

## Example Project Structure

JLens works best with Java projects following standard J2EE conventions:

```
project-root/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   ├── com/
│   │   │   │   └── example/
│   │   │   │       ├── controller/
│   │   │   │       ├── service/
│   │   │   │       ├── repository/
│   │   │   │       ├── model/
│   │   │   │       └── config/
│   │   ├── resources/
│   │   └── webapp/
│   └── test/
├── pom.xml
└── ...
```

## Project Understanding Capabilities

JLens can help you understand:

- Project architecture and organization
- API endpoints and methods
- Class dependencies and relationships
- Data flow and service interactions
- Batch processing components

## Output Formats

- Interactive web visualizations
- CSV/JSON data exports
- Network graphs for relationships
- Class and sequence diagrams
- Tabular data representations

## Troubleshooting

- **Parse Errors**: Some complex Java files may generate parsing errors, but JLens will continue analyzing other files
- **Memory Issues**: Large projects may require additional memory, use `--server.maxUploadSize=1024` to allow larger uploads
- **Display Issues**: For better diagram visualization, use a modern browser with JavaScript enabled

## Contributing

Contributions to improve JLens are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed changes

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Developed by Zensar Diamond Team

© 2025 JLens - All rights reserved