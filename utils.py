import pandas as pd
import os
import base64
import json
from io import BytesIO
import plotly.graph_objects as go

def create_data_tables(data):
    """
    Convert a list of dictionaries to a pandas DataFrame for display.
    
    Args:
        data: List of dictionaries or a DataFrame.
        
    Returns:
        pd.DataFrame: DataFrame ready for display in Streamlit.
    """
    if isinstance(data, pd.DataFrame):
        return data
    
    if not data:
        return pd.DataFrame()
    
    if isinstance(data, list):
        return pd.DataFrame(data)
    
    # If data is a dictionary of lists, convert to DataFrame
    if isinstance(data, dict):
        result = []
        for key, values in data.items():
            for value in values:
                if isinstance(value, dict):
                    value['group'] = key
                    result.append(value)
                else:
                    result.append({'group': key, 'value': value})
        return pd.DataFrame(result)
    
    # Fallback: return empty DataFrame
    return pd.DataFrame()

def get_file_content(file_path):
    """
    Read the content of a file.
    
    Args:
        file_path (str): Path to the file.
        
    Returns:
        str: Content of the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def get_java_file_type(file_path):
    """
    Determine the type of Java file based on its content and name.
    
    Args:
        file_path (str): Path to the Java file.
        
    Returns:
        str: Type of the Java file (e.g., "Entity", "Controller", "Service").
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        file_name = os.path.basename(file_path)
        
        # Check for common patterns in filename and content
        if 'Entity' in file_name or '@Entity' in content:
            return 'Entity'
        elif 'Controller' in file_name or '@Controller' in content or '@RestController' in content:
            return 'Controller'
        elif 'Service' in file_name or '@Service' in content:
            return 'Service'
        elif 'Repository' in file_name or '@Repository' in content:
            return 'Repository'
        elif 'DTO' in file_name or 'DataTransferObject' in file_name:
            return 'DTO'
        elif 'Job' in file_name or '@Scheduled' in content:
            return 'Batch/Job'
        elif 'Config' in file_name or '@Configuration' in content:
            return 'Configuration'
        elif 'Test' in file_name or '@Test' in content:
            return 'Test'
        elif 'Main' in file_name or 'public static void main' in content:
            return 'Main Class'
        elif 'Exception' in file_name:
            return 'Exception'
        elif 'Util' in file_name or 'Utils' in file_name:
            return 'Utility'
        else:
            return 'Other'
    except Exception:
        return 'Unknown'

def extract_package_structure(java_files):
    """
    Extract the package structure from a list of Java files.
    
    Args:
        java_files (list): List of Java file paths.
        
    Returns:
        dict: Hierarchical structure of packages.
    """
    package_structure = {}
    
    for file_path in java_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.readlines()
                
            # Look for package declaration
            package_name = None
            for line in content:
                if line.strip().startswith('package '):
                    package_name = line.strip().replace('package ', '').replace(';', '').strip()
                    break
            
            if not package_name:
                package_name = 'default'
            
            # Add to package structure
            if package_name not in package_structure:
                package_structure[package_name] = []
                
            package_structure[package_name].append(os.path.basename(file_path))
            
        except Exception:
            continue
    
    return package_structure

def get_csv_download_link(df, filename="data.csv", text="Download CSV"):
    """
    Generate a link to download a DataFrame as a CSV file.
    
    Args:
        df (pd.DataFrame): DataFrame to download.
        filename (str): Name of the downloaded file.
        text (str): Text to display for the download link.
        
    Returns:
        str: HTML link for downloading the CSV.
    """
    if df.empty:
        return ""
    
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def get_json_download_link(data, filename="data.json", text="Download JSON"):
    """
    Generate a link to download data as a JSON file.
    
    Args:
        data: Data to convert to JSON and download.
        filename (str): Name of the downloaded file.
        text (str): Text to display for the download link.
        
    Returns:
        str: HTML link for downloading the JSON.
    """
    if not data:
        return ""
    
    json_str = json.dumps(data, indent=2)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="{filename}">{text}</a>'
    return href

def get_figure_download_link(fig, filename="figure.png", text="Download Image"):
    """
    Generate a link to download a Plotly figure as a PNG image.
    
    Args:
        fig (go.Figure): Plotly figure to download.
        filename (str): Name of the downloaded file.
        text (str): Text to display for the download link.
        
    Returns:
        str: HTML link for downloading the image.
    """
    if not fig or not isinstance(fig, go.Figure):
        return ""
    
    # Convert plot to PNG
    buffer = BytesIO()
    fig.write_image(buffer, format="png", width=1200, height=800)
    buffer.seek(0)
    img_data = buffer.read()
    
    # Convert to base64
    b64 = base64.b64encode(img_data).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">{text}</a>'
    return href

def format_tree_data_for_csv(structure):
    """
    Format hierarchical tree data for CSV export.
    
    Args:
        structure (dict): Hierarchical structure data.
        
    Returns:
        pd.DataFrame: Flattened data ready for CSV export.
    """
    rows = []
    
    def traverse(node, path=""):
        if isinstance(node, dict):
            for key, value in node.items():
                new_path = f"{path}/{key}" if path else key
                traverse(value, new_path)
        elif isinstance(node, list):
            for item in node:
                if isinstance(item, dict) or isinstance(item, list):
                    traverse(item, path)
                else:
                    rows.append({"path": path, "item": item})
        else:
            rows.append({"path": path, "item": node})
    
    traverse(structure)
    return pd.DataFrame(rows)
