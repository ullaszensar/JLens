import pandas as pd
import os

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
