# JLens - Simple Setup Guide

## Quick Installation Steps

1. **Prerequisites**
   - Python 3.8 or higher
   - pip (Python package manager)

2. **Install Required Packages**
   ```bash
   pip install streamlit pandas plotly javalang networkx pygraphviz
   ```

3. **Run the Application**
   ```bash
   streamlit run app.py
   ```

4. **Access the Application**
   - Open your browser and go to: http://localhost:5000

## Project Files and Structure

```
jlens/
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── app.py                   # Main application entry point
├── java_parser.py           # Java code parsing functionality
├── uml_class_diagram.py     # UML diagram generation
├── utils.py                 # Utility functions
├── visualizer.py            # Visualization functionality
├── dependencies.txt         # List of required packages
├── README.md                # Project documentation
├── DEPLOYMENT.md            # Deployment instructions
├── USER_GUIDE.md            # User guide
├── SIMPLE_SETUP.md          # This file (simple setup)
└── attached_assets/         # Images and resources
```

## Key Files and Their Purpose

- **app.py**: Main Streamlit application with user interface and tabs
- **java_parser.py**: Handles parsing Java code to extract classes, methods, APIs
- **uml_class_diagram.py**: Generates class structure information
- **utils.py**: Helper functions for data processing and conversion
- **visualizer.py**: Creates visualizations for project structure and relationships

## Required Packages

1. streamlit - Web application framework
2. pandas - Data handling and analysis
3. plotly - Interactive visualization
4. javalang - Java code parsing
5. networkx - Graph management
6. pygraphviz - Graph visualization

## Simple Usage Steps

1. Start the application with `streamlit run app.py`
2. Upload a ZIP file containing your Java J2EE project
3. Select which aspects of the project to analyze
4. Navigate through the tabs to view analysis results

## Available Analysis Features

- Project structure visualization
- API endpoint detection
- Class structure and relationships
- Batch process identification
- Sequence diagrams
- Functional flow diagrams

---

© 2025 JLens - Zensar Diamond Team