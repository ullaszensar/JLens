# JLens Setup Guide

This guide provides detailed instructions for setting up and running the JLens Java J2EE project analyzer.

## System Requirements

- Python 3.11 or higher
- pip package manager
- Graphviz (system dependency for pygraphviz)

## Installation Steps

### 1. Install Required Packages

Install the following Python packages:

```bash
# Install core dependencies
pip install streamlit pandas plotly networkx javalang

# For graph visualization (requires graphviz system package)
# On Ubuntu/Debian: sudo apt-get install graphviz graphviz-dev
# On macOS: brew install graphviz
pip install pygraphviz
```

### 2. Configure Streamlit

Create a configuration file for Streamlit to ensure proper deployment:

```bash
mkdir -p .streamlit
```

Create `.streamlit/config.toml` with the following content:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

### 3. Run the Application

Start the JLens application:

```bash
streamlit run app.py
```

The application will be available at http://localhost:5000

## Package Details

JLens requires the following Python packages:

### Core Packages

- **streamlit**: Web application framework for data apps
  - Used for: Creating the interactive web interface

- **pandas**: Data manipulation and analysis library
  - Used for: Structured data handling and DataFrame operations

- **plotly**: Interactive data visualization library
  - Used for: Creating sequence diagrams and flow visualizations

- **networkx**: Graph creation and manipulation
  - Used for: Building relationship graphs between components

### Java Analysis Packages

- **javalang**: Java source code parser for Python
  - Used for: Parsing Java files to extract class and method information

- **pygraphviz**: Python interface to Graphviz
  - Used for: Advanced graph visualization capabilities

## Troubleshooting

### Common Issues

1. **Pygraphviz Installation Errors**:
   - Ensure Graphviz is installed on your system before installing pygraphviz
   - On some systems, you may need to specify include and library paths:
     ```
     pip install pygraphviz --global-option=build_ext --global-option="-I/usr/include/graphviz" --global-option="-L/usr/lib/graphviz/"
     ```

2. **Java Parsing Errors**:
   - Some Java files may not parse correctly if they use custom annotations or complex syntax
   - These errors are logged but don't prevent analysis from continuing

3. **Display Issues**:
   - If diagrams don't render correctly, try a different browser (Chrome recommended)
   - Ensure your browser window is wide enough for complex visualizations

## Deployment

For production deployment, consider:

1. Using Docker to containerize the application
2. Setting up proper authentication for production use
3. Configuring resource limits for handling large Java projects

## Support

For additional support or to report issues, contact the Zensar Diamond Team.