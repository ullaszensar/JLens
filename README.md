# JLens - Java J2EE Project Analyzer

JLens is a tool for analyzing Java J2EE projects, providing visualizations and structure analysis to help understand complex Java applications.

## Quick Setup

1. **Install dependencies:**
   ```bash
   pip install streamlit pandas plotly javalang networkx pygraphviz
   ```

2. **Run the application:**
   ```bash
   streamlit run app.py
   ```

3. **Access JLens** at http://localhost:5000

## Project Structure

```
jlens/
├── app.py                   # Main application
├── java_parser.py           # Java code parser
├── uml_class_diagram.py     # Class diagram generator
├── utils.py                 # Utility functions
├── visualizer.py            # Visualization tools
└── .streamlit/              # Configuration
```

## Features

- Project structure visualization
- API endpoint detection
- Class structure and relationships
- Batch process identification
- Sequence diagrams
- Functional flow mapping

## Usage

1. Upload a Java J2EE project ZIP file
2. Select analysis options
3. View results in the different tabs:
   - Project Structure
   - APIs
   - Functions
   - Batch Processes
   - Sequence Diagram
   - Functional Flow
4. Export data using the download buttons

## Required Packages

- streamlit - Web application framework
- pandas - Data handling
- plotly - Visualization
- javalang - Java parsing
- networkx - Graph creation
- pygraphviz - Graph visualization

## Documentation

- **SIMPLE_SETUP.md** - Quick installation guide
- **USER_GUIDE.md** - Detailed usage instructions
- **DEPLOYMENT.md** - Deployment options

## Support

For more details, see the other documentation files or contact the development team.

---

© 2025 JLens - Zensar Diamond Team