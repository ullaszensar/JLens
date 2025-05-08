# JLens Installation Guide

## Required Packages
```
streamlit==1.27.0
pandas==2.0.3
plotly==5.18.0
javalang==0.13.0
networkx==3.1
pygraphviz==1.11
```

## Installation Steps

1. Ensure Python 3.8+ is installed
2. Run:
   ```bash
   pip install streamlit pandas plotly javalang networkx pygraphviz
   ```

## Starting the Application

```bash
streamlit run app.py
```

## Access URL
http://localhost:5000

## Project Structure
- app.py - Main application
- java_parser.py - Java code parser
- uml_class_diagram.py - Class diagram generator
- utils.py - Utility functions
- visualizer.py - Visualization functions
- .streamlit/config.toml - Streamlit configuration

## Usage
1. Upload Java J2EE project ZIP file
2. Select analysis options
3. View results in tabs

© 2025 JLens - Zensar Diamond Team